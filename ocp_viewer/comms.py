"""ocp_viewer's transport: the websocket client, pointed at this viewer.

The client itself is `ocp_viewer_core.websocket`, shared with ocp_vscode - both
talk to a viewer over the same protocol, and this package needs no more of a
difference than which one it found. Named and shaped like ocp_vscode's comms.py
on purpose: the two hosts are maintained together.

The server's own transport - the browser at the other end of its websocket - is
`server/browser.py`, and is a different thing despite the similar name: this
one dials out to a viewer, that one answers the page it is serving.
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

__all__ = ["comms", "get_port", "set_port"]

# The one client this process talks to a viewer with, and what `show` is bound
# through. A module-level instance rather than module-level state.
comms = WebSocketComms()


def set_port(port, host=DEFAULT_HOST):
    """Skip discovery and pin to a viewer."""
    comms.set_port(port, host)


def get_port():
    """The port in use, discovering one on first call."""
    return comms.port
