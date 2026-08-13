"""The one websocket, and the six kinds of message that arrive on it.

Both ends of the viewer meet here. A user's Python process sends models,
config and commands; the browser sends back what the user did to the viewer.
The first byte says which, and this is the only place that knows the encoding -
everything above it works in objects.

Relaying is deliberately done without decoding: a model is large, the browser
wants exactly the bytes Python sent, and parsing it here would cost a copy of
the whole thing to learn nothing.
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

import orjson
import pyperclip
from ocp_viewer_core.comms import MessageType

from .screenshot import save_png_data_url

# The first byte of every message. `MessageType` is the shared vocabulary; this
# is how it is spelled on this wire.
COMMAND = "C"
DATA = "D"
UPDATE = "U"
CONFIG = "S"
LISTEN = "L"
BACKEND = "B"


def handle(viewer, ws):
    """Serve one connection until it closes."""
    while True:
        raw = ws.receive()
        if raw is None:
            return
        if isinstance(raw, bytes):
            raw = raw.decode("utf-8")

        kind, payload = raw[0], raw[2:]

        if kind == COMMAND:
            _command(viewer, ws, payload)
        elif kind == DATA:
            _model(viewer, ws, payload)
        elif kind == CONFIG:
            _config(viewer, ws, payload)
        elif kind == UPDATE:
            _update(viewer, ws, payload)
        elif kind == LISTEN:
            viewer.browser = ws
            print("Info: Browser as viewer client registered")
        elif kind == BACKEND:
            viewer.backend.handle_event(orjson.loads(payload)["model"], MessageType.DATA)
            ws.send(orjson.dumps({"ok": True}))


def _to_browser(viewer, payload):
    """Relay a message from Python to the browser, exactly as it arrived."""
    if viewer.browser is None:
        viewer.no_browser()
        return False
    viewer.browser.send(payload)
    return True


def _command(viewer, ws, payload):
    viewer.python = ws
    cmd = orjson.loads(payload)

    if cmd == "status":
        viewer.log("Received status command")
        ws.send(orjson.dumps({"command": "status", "text": viewer.status}))

    elif cmd == "config":
        viewer.log("Received config command")
        ws.send(orjson.dumps(viewer.reconfigure()))

    elif isinstance(cmd, dict) and cmd.get("type") in ("screenshot", "set_relative_time"):
        viewer.log(f"Received {cmd['type']} command")
        _to_browser(viewer, payload)


def _model(viewer, ws, payload):
    viewer.python = ws
    viewer.log("Received a new model")
    if _to_browser(viewer, payload):
        # The logo is on screen until the first model that is not it.
        viewer.splash = False


def _config(viewer, ws, payload):
    viewer.python = ws
    viewer.log("Received a config")
    if _to_browser(viewer, payload):
        viewer.log("Posted config to view")


def _update(viewer, ws, payload):
    viewer.browser = ws
    message = orjson.loads(payload)
    command = message.get("command")

    if command == "screenshot":
        save_png_data_url(message["text"]["data"], message["text"]["filename"])
    elif command == "log":
        viewer.log("[log]", message["text"])
    elif command == "started":
        viewer.log("Viewer has started")
    else:
        changes = message["text"]
        viewer.record(changes)
        if "selected" in changes:
            pyperclip.copy(",".join(changes["selected"]))

        # The backend answers by returning, and this is the half of the
        # conversation holding the browser's socket - so delivering is here.
        # None is the common case: any change set with no active tool, no
        # selection, or a selection the active tool cannot use.
        response = viewer.backend.handle_event(changes, MessageType.UPDATES)
        if response is not None:
            # Decoded, because a browser is on the other end: bytes go out as a
            # binary frame and arrive as a Blob, and the page reads what it is
            # given as text. Every other message here is relayed as the string
            # it arrived as, so this is the only one that has to be encoded.
            _to_browser(viewer, orjson.dumps(response).decode("utf-8"))
