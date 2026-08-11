"""The standalone OCP CAD viewer: a Flask app and the transport it speaks.

Everything the viewer *decides* is ocp-viewer-core's - the show pipeline, the
config semantics, the render and camera policy, the measurement backend, the
port registry and the wire protocol. What is here is a server: a page, a
websocket, and the settings that reach them.

`create_app` is the factory; `serve` is what the command line calls.
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

from flask import Flask, cli
from flask_sock import Sock
from ocp_viewer_core.comms import Session
from ocp_viewer_core.config import (
    AnalysisTool,
    Camera,
    Collapse,
    Config,
    Render,
    StudioBackground,
    StudioEnvironment,
    StudioTextureMapping,
    StudioToneMapping,
    UiTab,
)
from ocp_viewer_core.logo import logo
from ocp_viewer_core.show import Viewer as CoreViewer
from ocp_viewer_core.state import add_port, del_port
from ocp_viewer_core.websocket import WebSocketComms

from ._version import __version__
from .keys import EXCLUDE_KEYS, WORKSPACE_CONFIG_KEYS
from .network import is_port_in_use
from .sockets import handle
from .viewer import Viewer
from .views import bp

# ------------------------------------------------------------------------
# The client half: `from ocp_viewer import show`.
#
# This package is both the viewer and the way to draw into it, which is what
# every host of the core is. The alternative was importing `show` from
# ocp_vscode - installing the VS Code package to use the standalone, and
# depending on a sibling host, which is exactly what the split undoes.
#
# Six lines, because everything they name is shared: the transport is the
# websocket client, and the show family is the core's Viewer bound to it.
# ------------------------------------------------------------------------

client = WebSocketComms()
_session = Session(client)
config = Config(_session, WORKSPACE_CONFIG_KEYS, EXCLUDE_KEYS)
_viewer = CoreViewer[None](config)

show = _viewer.show
show_object = _viewer.show_object
show_objects = _viewer.show_objects
show_all = _viewer.show_all
show_clear = _viewer.show_clear
push_object = _viewer.push_object
remove_object = _viewer.remove_object
reset_show = _viewer.reset_show
save_screenshot = _viewer.save_screenshot
get_colormap = _viewer.get_colormap
set_colormap = _viewer.set_colormap
unset_colormap = _viewer.unset_colormap
get_last_paths = _viewer.get_last_paths

set_defaults = config.set_defaults
set_viewer_config = config.set_viewer_config


def set_port(port, host="127.0.0.1"):
    """Skip discovery and pin to a viewer."""
    client.set_port(port, host)


def get_port():
    """The port in use, discovering one on first call."""
    return client.port


def status(port=None, debug=False):
    """Get viewer status"""
    _session.begin({"port": port})
    try:
        return config.status(debug=debug)
    finally:
        _session.clear()


def workspace_config(port=None):
    """Get viewer workspace config"""
    _session.begin({"port": port})
    try:
        return config.workspace_config()
    finally:
        _session.clear()


def combined_config(port=None):
    """Get combined config from workspace and status"""
    _session.begin({"port": port})
    try:
        return config.combined_config()
    finally:
        _session.clear()


def get_defaults(port=None):
    """Get all defaults"""
    _session.begin({"port": port})
    try:
        return config.get_defaults()
    finally:
        _session.clear()


def get_default(key, port=None):
    """Get default value for key"""
    _session.begin({"port": port})
    try:
        return config.get_default(key)
    finally:
        _session.clear()


def reset_defaults(port=None):
    """Reset defaults not given in workspace config"""
    _session.begin({"port": port})
    try:
        return config.reset_defaults()
    finally:
        _session.clear()


__all__ = [
    "AnalysisTool",
    "Camera",
    "Collapse",
    "Render",
    "StudioBackground",
    "StudioEnvironment",
    "StudioTextureMapping",
    "StudioToneMapping",
    "UiTab",
    "Viewer",
    "__version__",
    "combined_config",
    "create_app",
    "get_default",
    "get_defaults",
    "get_port",
    "push_object",
    "remove_object",
    "reset_defaults",
    "reset_show",
    "save_screenshot",
    "serve",
    "set_defaults",
    "set_port",
    "set_viewer_config",
    "show",
    "show_all",
    "show_clear",
    "show_object",
    "show_objects",
    "status",
    "workspace_config",
]


def _no_banner(debug: bool, app_import_path: str | None) -> None:
    """Flask's banner, silenced."""


def create_app(params):
    """Build the app and the viewer it serves.

    The viewer lives in `app.extensions`, which is where a Flask extension's
    state belongs and what makes two viewers in one process two viewers.
    """
    viewer = Viewer(params)

    if not viewer.debug:
        # Flask prints a development-server banner on start and offers no
        # option to turn it off; replacing the function that prints it is the
        # way. A named function rather than a lambda, so it has the signature
        # the attribute is declared with.
        # The ignore is about the assignment itself, not the signature: ty
        # treats a module-level `def` as a binding rather than a variable, so
        # replacing one is an error however well the replacement matches. The
        # alternative is calling werkzeug's run_simple instead of app.run and
        # skipping the banner that way, which is a change to the startup path
        # and not one to make while moving code.
        cli.show_server_banner = _no_banner  # ty: ignore[invalid-assignment]
        logging.getLogger("werkzeug").setLevel(logging.ERROR)

    app = Flask(__name__)
    app.extensions["ocp_viewer"] = viewer
    app.register_blueprint(bp)

    sock = Sock(app)
    sock.route("/")(lambda ws: handle(viewer, ws))

    return app


def serve(params):
    """Run the viewer until it is stopped."""
    app = create_app(params)
    viewer = app.extensions["ocp_viewer"]

    if is_port_in_use(viewer.port, viewer.host):
        print(
            f"Port {viewer.port} is already in use. Please choose a different "
            "port or stop the other service using this port."
        )
        sys.exit(1)

    # The logo is measurable from the moment the viewer opens, before any model
    # has been shown - which is what loading it into the backend buys.
    viewer.backend.load_model(logo)

    add_port(viewer.port)
    atexit.register(del_port, viewer.port)

    print(f"Info: OCP Viewer runs at http://{viewer.host}:{viewer.port}")
    app.run(port=viewer.port, host=viewer.host, debug=viewer.debug, use_reloader=False)
