"""The HTTP side of the server: the page, the files it loads, and `/`.

`websockets` serves websocket connections and offers one hook for everything
else: `process_request`, which may answer a request itself instead of handing
it on to the opening handshake. Three answers are needed - the page, the files
under `static/`, and a redirect from `/` to the page - so this module is the
whole web server, and there is no framework in front of it.
"""

#
# Copyright 2026 Bernhard Walter
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import email.utils
import json
import mimetypes
from http import HTTPStatus
from pathlib import Path
from string import Template

from websockets.datastructures import Headers
from websockets.http11 import Response

ROOT = Path(__file__).parent
TEMPLATE = ROOT / "templates" / "viewer.html"
STATIC = (ROOT / "static").resolve()


def respond(viewer, request):
    """Answer a plain HTTP request, or None to let the websocket handshake run.

    The `process_request` hook, with the viewer bound. A request that asks to
    upgrade is the browser's websocket (or Python's), and is not ours.
    """
    if request.headers.get("Upgrade", "").lower() == "websocket":
        return None

    path = request.path.partition("?")[0]
    if path == "/":
        return _response(HTTPStatus.FOUND, b"", "text/plain", {"Location": "/viewer"})
    if path == "/viewer":
        return _response(HTTPStatus.OK, _page(viewer, request), "text/html; charset=utf-8")
    if path.startswith("/static/"):
        return _asset(path[len("/static/") :])
    return _response(HTTPStatus.NOT_FOUND, b"Not found\n", "text/plain; charset=utf-8")


def _page(viewer, request):
    """The page, with this viewer's settings and the address to dial back."""
    # The websocket address is taken from the request rather than from how this
    # server was started: a browser may have reached it by a hostname that is
    # routable from where it is, and that is the address it must dial back.
    #
    # partition rather than split, because the Host header carries no port when
    # the port is the scheme's default - behind a proxy, or on 80. An empty
    # port is what comms.js already treats as "the default one".
    address, _, port = request.headers.get("Host", "").partition(":")

    # Every placeholder is a JSON literal, so the page reads a value of the
    # right type and no quoting is done by hand. The one exception is the
    # reconnect limit: absent, it is left to comms.js's own default rather than
    # repeated here.
    attempts = viewer.max_reconnect_attempts
    values = {
        "ws_host": json.dumps(address),
        "ws_port": json.dumps(port),
        "max_retries": "undefined" if attempts is None else json.dumps(attempts),
        "theme": json.dumps(viewer.config["theme"]),
        "tree_width": json.dumps(viewer.config["tree_width"]),
        "glass": json.dumps(viewer.config["glass"]),
        "tools": json.dumps(viewer.config["tools"]),
        "up": json.dumps(viewer.config["up"]),
        "control": json.dumps(viewer.config["control"]),
        "modifier_keys": json.dumps(viewer.config["modifier_keys"]),
    }
    # `substitute`, not `safe_substitute`: a placeholder the page names and this
    # dict does not fill is a defect, and should fail here rather than reach a
    # browser as a literal dollar sign.
    with open(TEMPLATE, encoding="utf-8") as f:
        return Template(f.read()).substitute(values).encode("utf-8")


def _asset(name):
    """A file under static/, and nothing outside it."""
    file = (STATIC / name).resolve()
    if not file.is_relative_to(STATIC) or not file.is_file():
        return _response(HTTPStatus.NOT_FOUND, b"Not found\n", "text/plain; charset=utf-8")
    content_type = mimetypes.guess_type(file.name)[0] or "application/octet-stream"
    # no-cache: revalidate on every load, so a rebuilt renderer or a bumped core
    # is what the next reload shows. The files are local and small enough for
    # that to cost nothing noticeable.
    return _response(HTTPStatus.OK, file.read_bytes(), content_type, {"Cache-Control": "no-cache"})


def _response(status, body, content_type, extra=None):
    """One HTTP/1.1 response, closing the connection after it.

    The headers `websockets` itself puts on a rejection, plus ours: it serializes
    exactly what it is given, so Content-Length is this function's to write.
    """
    headers = Headers(
        [
            ("Date", email.utils.formatdate(usegmt=True)),
            ("Connection", "close"),
            ("Content-Length", str(len(body))),
            ("Content-Type", content_type),
        ]
    )
    for key, value in (extra or {}).items():
        headers[key] = value
    return Response(status.value, status.phrase, headers, body)
