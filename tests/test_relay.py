"""The server relays Python's messages to the browser intact and in order.

The regression this guards: a config sent right behind a large model reached
the browser first and unreadable, because the old server compressed and wrote
the browser's socket from several threads with nothing serializing them. The
browser here is a `websockets` client that registers exactly as the page does.
"""

import base64
import os
import subprocess
import sys
import time

import orjson
import pytest
from ocp_viewer_core.state import del_port
from ocp_viewer_core.websocket import port_check
from websockets.sync.client import connect

# Its own port, so that this module and test_cli.py never meet on one.
PORT = 39778
STARTUP_TIMEOUT = 20.0


@pytest.fixture
def standalone():
    """`python -m ocp_viewer` on PORT, ready to answer; killed afterwards."""
    env = dict(os.environ)
    env.pop("OCP_PORT", None)
    proc = subprocess.Popen(
        [sys.executable, "-m", "ocp_viewer", "--port", str(PORT)],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    deadline = time.time() + STARTUP_TIMEOUT
    while not port_check(PORT):
        if proc.poll() is not None:
            raise AssertionError(
                f"standalone exited with {proc.returncode}:\n{proc.stdout.read()}"
            )
        if time.time() > deadline:
            proc.kill()
            raise AssertionError(f"standalone did not listen on {PORT} in time")
        time.sleep(0.2)
    yield proc
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
    del_port(PORT)


def _python_sends(payload):
    """One message the way the core's client sends it: a connection of its own."""
    with connect(f"ws://127.0.0.1:{PORT}", close_timeout=0.05, max_size=None) as ws:
        ws.send(payload)


def test_config_behind_a_large_model_arrives_after_it(standalone):
    # Base64 of random bytes, as a model with textures is: something a deflate
    # pass has to work on for seconds, which is the window the old server lost
    # the ordering in. 40 MB on the wire.
    blob = base64.b64encode(os.urandom(30 * 1024 * 1024)).decode("ascii")
    model = orjson.dumps({"type": "data", "blob": blob})
    config = orjson.dumps({"type": "ui", "config": {"tab": "studio"}})

    with connect(f"ws://127.0.0.1:{PORT}", max_size=None) as browser:
        browser.send("L:{}")

        _python_sends(b"D:" + model)
        _python_sends(b"S:" + config)

        first = browser.recv(timeout=60)
        second = browser.recv(timeout=60)

    assert first == model.decode("utf-8")
    assert second == config.decode("utf-8")
