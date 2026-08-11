"""Is something already listening?

Its own module because it is the one piece here that is neither Flask nor the
viewer: a dual-stack check that has to try both IPv4 and IPv6, because a server
bound to one can answer on the other and a single check reports a free port
that is not.
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

import socket


def is_port_in_use(port, host="127.0.0.1"):
    """
    Check if a port is in use on both IPv4 and IPv6 localhost.

    This function checks multiple addresses to handle dual-stack scenarios
    where a server might be listening on IPv6 and accepting IPv4 connections.

    Args:
        port: The port number to check
        host: The host to check (default: "127.0.0.1")

    Returns:
        True if the port is in use on either IPv4 or IPv6, False otherwise
    """
    import errno as errno_module
    import sys

    hosts_to_check = []

    # Determine which hosts to check based on the requested host
    if host == "127.0.0.1" or host == "localhost":
        # Check both IPv4 and IPv6 localhost
        hosts_to_check = [
            ("127.0.0.1", socket.AF_INET),
            ("::1", socket.AF_INET6),
        ]
    elif host == "0.0.0.0":
        # Check all interfaces (both IPv4 and IPv6)
        hosts_to_check = [
            ("0.0.0.0", socket.AF_INET),
            ("::", socket.AF_INET6),
        ]
    else:
        # For specific hosts, determine the address family
        try:
            info = socket.getaddrinfo(host, port, socket.AF_UNSPEC, socket.SOCK_STREAM)
            if info:
                family = info[0][0]
                hosts_to_check = [(host, family)]
        except socket.gaierror:
            # If we can't resolve the host, try IPv4 by default
            hosts_to_check = [(host, socket.AF_INET)]

    for check_host, family in hosts_to_check:
        # First try a connection test (more reliable, especially on Windows)
        try:
            test_sock = socket.socket(family, socket.SOCK_STREAM)
            test_sock.settimeout(0.5)
            result = test_sock.connect_ex((check_host, port))
            test_sock.close()

            # If connection succeeds or is refused, port is in use
            if result == 0:  # Connected successfully
                return True
            # ECONNREFUSED means nothing is listening, port is free
            # Any other error, we'll fall through to the bind test
        # Best effort: a failed connection test says nothing either way, and
        # the bind test below is the one that decides.
        except (TimeoutError, OSError):
            pass

        # Bind test - try to bind to the port
        try:
            bind_sock = socket.socket(family, socket.SOCK_STREAM)
            # SO_REUSEADDR allows binding to TIME_WAIT sockets
            bind_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            # For IPv6, try to set IPV6_V6ONLY to avoid dual-stack issues
            if family == socket.AF_INET6 and hasattr(socket, "IPV6_V6ONLY"):
                try:
                    bind_sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 1)
                except OSError:
                    pass  # Not critical if this fails

            bind_sock.bind((check_host, port))
            bind_sock.close()
        except OSError as e:
            # Check for EADDRINUSE across platforms
            # macOS: errno.EADDRINUSE = 48
            # Linux: errno.EADDRINUSE = 98
            # Windows: errno.WSAEADDRINUSE = 10048
            if e.errno == errno_module.EADDRINUSE or (
                sys.platform == "win32" and e.errno == 10048
            ):
                return True
            # Other errors (like EADDRNOTAVAIL for IPv6 when disabled)
            # are not definitive, so continue checking
        # Anything else is not evidence that the port is taken, so the other
        # addresses still get their turn.
        except Exception:  # noqa: BLE001, S110
            pass
        finally:
            # Bare, because bind_sock may not exist: if socket() itself raised,
            # the name was never bound and this is a NameError rather than
            # anything socket-shaped.
            try:
                bind_sock.close()
            except:  # noqa: E722, S110
                pass

    return False
