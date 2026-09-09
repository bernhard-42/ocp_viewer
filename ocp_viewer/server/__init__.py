"""The server half: a page, a websocket, and the settings that reach them.

A subpackage of its own because only this host has one - the VS Code extension
serves its viewer itself. The client half above, `comms`, `config` and `show`,
is named as ocp_vscode names it, so that a fix in one is findable in the
other.

The server is `websockets`' threaded one, the same library the client half
already speaks through. It answers websocket connections with `sockets.handle`
and everything else - the page, its files - through `pages.respond`.
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

import atexit
import logging
import sys
import threading
import time

from ocp_viewer_core.logo import logo
from ocp_viewer_core.state import add_port, del_port
from websockets.exceptions import InvalidMessage
from websockets.sync.server import serve as websocket_server

from .network import is_port_in_use
from .pages import missing_assets, respond
from .sockets import handle
from .viewer import Viewer

__all__ = ["Viewer", "create_server", "serve"]


class _NotAProbe(logging.Filter):
    """Drop the traceback for a connection that said nothing.

    The core's `port_check` - every client's discovery, so every fresh `show()`
    - connects and closes without sending a byte. `websockets` reports that as
    a failed handshake with a full traceback, at ERROR, which would put one in
    the viewer's terminal per probe. A silent connection is not an error here;
    anything else that fails the handshake still prints.
    """

    def filter(self, record):
        exc = record.exc_info[1] if record.exc_info else None
        return not (isinstance(exc, InvalidMessage) and isinstance(exc.__cause__, EOFError))


def create_server(params):
    """The viewer and the server that serves it, bound but not yet running.

    Everything `serve` does that is not about this process - the port check,
    the registry, the banner - stays there, so a test can run the real server
    on a port of its own in a thread of its own.
    """
    viewer = Viewer(params)

    # Say it now rather than serve a page that loads nothing: the renderer and
    # the shared page logic are copied in by `make assets`, and a wheel built
    # from a checkout that never ran it - `uv add path/to/ocp-viewer` builds
    # one - ships without them.
    missing = missing_assets()
    if len(missing) > 0:
        print(
            "Warning: the viewer page cannot load, these files are missing from "
            "the installed package:\n  "
            + "\n  ".join(missing)
            + "\nThey are copied in by `make assets` (or `make dist`) in the "
            "ocp-viewer checkout before the package is built; a released wheel "
            "carries them."
        )

    logging.getLogger("websockets.server").addFilter(_NotAProbe())

    # The logo is measurable from the moment the viewer opens, before any model
    # has been shown - which is what loading it into the backend buys.
    viewer.backend.load_model(logo)

    server = websocket_server(
        lambda ws: handle(viewer, ws),
        viewer.host,
        viewer.port,
        process_request=lambda _connection, request: respond(viewer, request),
        # A model is JSON with base64 textures inside, which deflate shrinks by
        # a quarter at the cost of seconds of CPU on every show. The browser is
        # on the same machine, or a fast link; the seconds are what the user
        # notices.
        compression=None,
        # The default is 1 MiB, and a model is a good deal more than that.
        max_size=None,
    )
    return viewer, server


def serve(params):
    """Run the viewer until it is stopped."""
    host = params.get("host", "127.0.0.1")
    port = params.get("port", 3939)
    if is_port_in_use(port, host):
        print(
            f"Port {port} is already in use. Please choose a different "
            "port or stop the other service using this port."
        )
        sys.exit(1)

    if params.get("debug", False):
        # Every connection opening and closing, from the library's own logger.
        logging.basicConfig(level=logging.INFO)

    viewer, server = create_server(params)

    add_port(viewer.port)
    atexit.register(del_port, viewer.port)

    print(f"Info: OCP Viewer runs at http://{viewer.host}:{viewer.port}")

    # The server runs on a thread of its own and the main thread sleeps in a
    # loop, for Ctrl-C's sake. `serve_forever` blocks in a `select()` with no
    # timeout, and on Windows a Ctrl-C is delivered only between bytecodes -
    # never into a blocking call - so a server run on the main thread could not
    # be stopped there at all (measured: a bare select() never returned). On
    # POSIX the signal does interrupt the select, but the handler thread of a
    # connected page is not a daemon thread and kept the process alive after
    # the server had stopped; closing the browser's socket is what ends it.
    thread = threading.Thread(target=server.serve_forever, name="ocp-viewer-server", daemon=True)
    thread.start()
    try:
        while thread.is_alive():
            time.sleep(0.5)
    except KeyboardInterrupt:
        pass
    server.shutdown()
    if viewer.browser is not None:
        viewer.browser.close()
