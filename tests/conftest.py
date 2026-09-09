"""The real server, in this process, on a port of its own.

`create_server` is the seam: the same viewer, the same handlers and the same
server `python -m ocp_viewer` runs, minus the port registry and the banner.
Running it in a thread rather than a subprocess is what lets a test look at the
viewer object while messages are in flight - which browser is registered, what
the status holds - instead of inferring it through the wire.

`~/.ocpvscode_standalone` is redirected to a temporary path for every test, so
the developer's own file never reaches a test's config.
"""

import threading
import time

import orjson
import pytest
from websockets.sync.client import connect

from ocp_viewer.server import create_server
from ocp_viewer.server import settings as settings_module


@pytest.fixture(autouse=True)
def config_file(tmp_path, monkeypatch):
    """Where the settings module reads the user's file from: nowhere, unless a test writes one."""
    path = tmp_path / "ocpvscode_standalone"
    monkeypatch.setattr(settings_module, "CONFIG_FILE", path)
    return path


class Running:
    """A running standalone: its viewer, its port, and the two ways to talk to it."""

    def __init__(self, viewer, server):
        self.viewer = viewer
        self.server = server
        self.port = server.socket.getsockname()[1]
        self.url = f"ws://127.0.0.1:{self.port}"
        self.http = f"http://127.0.0.1:{self.port}"

    def python(self, kind, payload, reply=False):
        """One message the way the core's client sends it: a connection per message.

        `payload` is bytes or an object to encode; `reply` reads one answer
        before closing, as a command does.
        """
        body = payload if isinstance(payload, bytes) else orjson.dumps(payload)
        with connect(self.url, close_timeout=0.05, max_size=None) as ws:
            ws.send(kind.encode("ascii") + b":" + body)
            if reply:
                return orjson.loads(ws.recv(timeout=10))
        return None

    def browser(self):
        """A connection registered as the page registers itself, once the server has it."""
        ws = connect(self.url, max_size=None)
        ws.send("L:{}")
        deadline = time.time() + 5
        while self.viewer.browser is None:
            assert time.time() < deadline, "the server never registered the browser"
            time.sleep(0.01)
        return ws

    def wait(self, predicate, timeout=5):
        """Block until the viewer satisfies `predicate` - a message handled on another thread."""
        deadline = time.time() + timeout
        while not predicate(self.viewer):
            assert time.time() < deadline, "timed out waiting on the viewer"
            time.sleep(0.01)


@pytest.fixture
def standalone():
    """`start(**params)` runs a server and returns a `Running`; all are stopped afterwards."""
    started = []

    def start(**params):
        viewer, server = create_server({"host": "127.0.0.1", "port": 0, **params})
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        started.append((server, thread))
        return Running(viewer, server)

    yield start

    for server, thread in started:
        server.shutdown()
        thread.join(timeout=5)
