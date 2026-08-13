"""What the running viewer knows: its clients, its config, and its state.

One object rather than module globals, so that two viewers in one process are
two viewers - the defect the same restructuring closed on the Python client
side. The Flask app holds it in `app.extensions`, which is where an extension's
state belongs.
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

from ocp_viewer_core.backend import ViewerBackend

from .settings import resolve


class Viewer:
    """The state one running viewer has."""

    def __init__(self, params):
        self.params = params
        self.debug = params.get("debug", False)
        self.host = params.get("host", "127.0.0.1")
        self.port = params.get("port", 3939)
        self.max_reconnect_attempts = params.get("max_reconnect_attempts")

        self.config = resolve(params)
        self.status = {}
        self.last_changes = {}

        # The two ends: a user's Python process, and the browser. Either can
        # come and go, and both are recorded when they first say something.
        self.python = None
        self.browser = None

        # True until the first real model arrives, which is what tells the
        # config call that the logo is still on screen.
        self.splash = True

        # No transport: the backend computes and returns, and `sockets._update`
        # - which already holds the browser's socket - is what delivers.
        self.backend = ViewerBackend()

    def log(self, *message):
        if self.debug:
            print("Debug:", *message)

    def no_browser(self):
        print(
            "\nNo browser registered. Please open the viewer in a browser "
            "or refresh the viewer page\n"
        )

    def reconfigure(self):
        """Re-read the settings, for a client asking what they are now."""
        self.config = resolve(self.params)
        self.config["_splash"] = self.splash
        return self.config

    def record(self, changes):
        """Take the browser's report of what changed, and keep the picture."""
        diff = {
            key: value
            for key, value in changes.items()
            if key not in self.last_changes or self.last_changes[key] != value
        }
        if diff:
            self.log("Incremental UI changes", diff)
        self.last_changes = dict(changes)
        self.status.update(changes)
        return diff
