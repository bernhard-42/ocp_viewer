"""`is_port_in_use`: a listening socket is found, a free port is not."""

import socket

from ocp_viewer.server.network import is_port_in_use


def test_a_bound_port_is_in_use_and_a_released_one_is_not():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        s.listen(1)
        port = s.getsockname()[1]
        assert is_port_in_use(port) is True
    assert is_port_in_use(port) is False
