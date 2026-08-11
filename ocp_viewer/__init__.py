"""The standalone OCP CAD viewer: draw into it, and serve it.

`from ocp_viewer import show` is the client, and `python -m ocp_viewer` is the
server. Everything the viewer decides is `ocp-viewer-core`'s, shared with
ocp_vscode, Jupyter CadQuery and build123d Studio.

comms.py, config.py and show.py are named and shaped as ocp_vscode's are: the
two packages are maintained together, and a fix in one should be findable in
the other. The server half, which ocp_vscode has no counterpart for, is under
`server/`.
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

# ruff: noqa: F401

from ._version import __version__
from .comms import *
from .config import *
from .show import *
