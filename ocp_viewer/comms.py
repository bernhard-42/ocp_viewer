"""ocp_viewer's transport: the websocket client, pointed at this viewer.

The client itself is `ocp_viewer_core.websocket`, shared with ocp_vscode - both
talk to a viewer over the same protocol, and this package needs no more of a
difference than which one it found. Named and shaped like ocp_vscode's comms.py
on purpose: the two hosts are maintained together.

The other one is `server/comms.py`, which faces the other way: this client is
told which viewer to talk to and opens a connection to it, and that one answers
the browser that connected to the server. `set_port` and `get_port` are here
rather than there because what they point is this one - the server's port is
where it listens, and is a startup setting rather than something a script
chooses.
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

from ocp_viewer_core.websocket import DEFAULT_HOST, WebSocketComms

__all__ = ["StandaloneComms", "comms", "get_port", "set_port"]


class StandaloneComms(WebSocketComms):
    """A viewer in a browser, reached over a websocket.

    Nothing to add to the shared client: this host and ocp_vscode speak the same
    protocol to the same kind of server, and the one difference ocp_vscode has -
    telling the user about an input box - is not this host's. Named for symmetry
    with the other hosts' transports, and so that anything this viewer comes to
    need has a place to go.
    """


# The one client this process talks to a viewer with, and what `show` is bound
# through. A module-level instance rather than module-level state.
comms = StandaloneComms()


def set_port(port, host=DEFAULT_HOST):
    """Skip discovery and pin to a viewer."""
    comms.set_port(port, host)


def get_port():
    """The port in use, discovering one on first call."""
    return comms.port
