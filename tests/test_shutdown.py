"""Ctrl-C stops the server, on every platform, with a page connected.

The real Ctrl-C is a console event and cannot be sent portably from a test;
`_thread.interrupt_main()` is what Python's own console handler does with it -
trips SIGINT and wakes a sleeping main thread - so a timer calling it inside the
server process is the same event at the level the server sees it. The failure
modes this guards were measured: on Windows a server run on the main thread
blocks in `select()` and never sees the interrupt at all; on POSIX it does, but
a connected page's handler thread kept the process alive afterwards.
"""

import os
import subprocess
import sys
import time

from ocp_viewer_core.state import del_port
from ocp_viewer_core.websocket import port_check
from websockets.sync.client import connect

PORT = 39780

SERVER = f"""
import threading, _thread
threading.Timer(3.0, _thread.interrupt_main).start()
from ocp_viewer.server import serve
serve({{"host": "127.0.0.1", "port": {PORT}}})
"""


def test_an_interrupt_ends_the_process_even_with_a_page_connected():
    env = dict(os.environ)
    env.pop("OCP_PORT", None)
    proc = subprocess.Popen(
        [sys.executable, "-c", SERVER],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    try:
        deadline = time.time() + 20
        while not port_check(PORT):
            assert proc.poll() is None, proc.stdout.read()
            assert time.time() < deadline, "the server did not come up"
            time.sleep(0.2)

        with connect(f"ws://127.0.0.1:{PORT}") as page:
            page.send("L:{}")
            try:
                proc.wait(timeout=15)
            except subprocess.TimeoutExpired:
                raise AssertionError("the server was still running 12 s after the interrupt") from None
        assert proc.returncode == 0, proc.stdout.read()
    finally:
        if proc.poll() is None:
            proc.kill()
        del_port(PORT)
