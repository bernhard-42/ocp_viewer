"""The standalone OCP CAD viewer: draw into it, and serve it.

`from ocp_viewer import show` is the client, and `python -m ocp_viewer` is the
server. Everything the viewer decides is `ocp-viewer-core`'s, shared with
ocp_vscode, Jupyter CadQuery and build123d Studio.

`comms.py`, `config.py` and `show.py` are named and shaped as ocp_vscode's
are, so that the two packages can be maintained together. The server half,
which only this host has, is under `server/`.
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

from ocp_viewer_core.tessellator import (
    ImageFace,
    disable_native_tessellator,
    enable_native_tessellator,
    init_native_tessellator,
    is_native_tessellator_enabled,
)
from ocp_viewer_core.colors import (
    BaseColorMap,
    ColorMap,
    GoldenRatioColormap,
    ListedColorMap,
    SeededColormap,
    SegmentedColorMap,
    hex_to_rgb,
    hsv_mapper,
    matplotlib_mapper,
    random_rgb_mapper,
    web_to_rgb,
)
from ocp_viewer_core.selectors import (
    select_edge,
    select_edges,
    select_face,
    select_faces,
    select_vertex,
    select_vertices,
)

from ._version import __version__
from .comms import *
from .config import *
from .show import *

# The union of the star-imported __all__s plus the explicit imports above, so
# the star surface is chosen rather than accidental. `comms` is the transport
# instance from comms.py's __all__, not the submodule.
__all__ = [
    "AnalysisTool",
    "Animation",
    "BaseColorMap",
    "Camera",
    "Collapse",
    "ColorMap",
    "combined_config",
    "comms",
    "disable_native_tessellator",
    "enable_native_tessellator",
    "find_and_set_port",
    "get_colormap",
    "get_default",
    "get_defaults",
    "get_last_paths",
    "get_port",
    "GoldenRatioColormap",
    "hex_to_rgb",
    "hsv_mapper",
    "ignore_camera_warnings",
    "ImageFace",
    "init_native_tessellator",
    "is_native_tessellator_enabled",
    "ListedColorMap",
    "matplotlib_mapper",
    "none_filter",
    "push_object",
    "random_rgb_mapper",
    "remove_object",
    "Render",
    "reset_defaults",
    "reset_show",
    "save_screenshot",
    "SeededColormap",
    "SegmentedColorMap",
    "select_edge",
    "select_edges",
    "select_face",
    "select_faces",
    "select_vertex",
    "select_vertices",
    "set_colormap",
    "set_defaults",
    "set_port",
    "set_viewer_config",
    "show",
    "show_all",
    "show_clear",
    "show_object",
    "show_objects",
    "StandaloneComms",
    "status",
    "StudioBackground",
    "StudioEnvironment",
    "StudioTextureMapping",
    "StudioToneMapping",
    "UiTab",
    "unset_colormap",
    "web_to_rgb",
    "workspace_config",
]


if init_native_tessellator():
    print("Found and enabled native tessellator.")
