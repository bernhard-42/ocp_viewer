"""This host's transport: the browser on the other end of a websocket.

The only class ocp_viewer implements from the core, and it is short because
this host is a server. A message does not have to be dialled anywhere - the
browser is already connected, and its socket is held by the running app.

Which is the difference from ocp_vscode's, and worth stating: there, `show()`
runs in the user's Python process and has to reach a viewer somewhere else, so
its Comms opens a websocket per message. Here the sending happens inside the
process the browser is talking to, so a send is a write to a socket already in
hand.
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
from ocp_viewer_core.comms import Comms


class BrowserComms(Comms[None]):
    """Answers the browser this server is serving.

    Built with the viewer so it can ask, at send time, which socket is
    registered - a browser can refresh, and the socket it had is not the socket
    it has. Holding the socket itself would answer with a closed one.

    Only `send_response` is implemented. The measurement backend is the one
    thing this host runs that talks *to* the browser; models, config and
    commands arrive from a user's Python process and are relayed by the socket
    handler, which has the message already encoded and no reason to decode it.
    """

    def __init__(self, viewer):
        super().__init__()
        self.viewer = viewer

    def send_response(self, data, timeit=False) -> None:
        client = self.viewer.browser
        if client is None:
            self.viewer.no_browser()
            return
        client.send(orjson.dumps(data))
