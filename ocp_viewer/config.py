"""Configuration of the viewer.

The semantics live in `ocp_viewer_core.config`. What is this host's, and stays
here, is the two lists that tell the core what it can do, and the names bound
off the Config built from them.

Deliberately the same file, the same lists and the same functions as
ocp_vscode's config.py. Both serve a three-cad-viewer of the same version, so
the keys its status reports are the same keys - and where the two packages do
the same job they should be the same to read.
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

from ocp_viewer_core.comms import Session
from ocp_viewer_core.config import (
    AnalysisTool,
    Camera,
    Collapse,
    Config,
    Render,
    StudioBackground,
    StudioEnvironment,
    StudioTextureMapping,
    StudioToneMapping,
    UiTab,
)

from ocp_viewer.comms import comms

__all__ = [
    "AnalysisTool",
    "Camera",
    "Collapse",
    "Render",
    "StudioBackground",
    "StudioEnvironment",
    "StudioTextureMapping",
    "StudioToneMapping",
    "UiTab",
    "combined_config",
    "get_default",
    "get_defaults",
    "reset_defaults",
    "set_defaults",
    "set_viewer_config",
    "status",
    "workspace_config",
]

WORKSPACE_CONFIG_KEYS = (
    "ambient_intensity",
    "analysis_tool",
    "angular_tolerance",
    "axes",
    "axes0",
    "black_edges",
    "center_grid",
    "clip_intersection",
    "clip_normal_0",
    "clip_normal_1",
    "clip_normal_2",
    "clip_object_colors",
    "clip_planes",
    "clip_slider_0",
    "clip_slider_1",
    "clip_slider_2",
    "collapse",
    "dark",
    "default_color",
    "default_edgecolor",
    "default_facecolor",
    "default_opacity",
    "default_thickedgecolor",
    "default_vertexcolor",
    "deviation",
    "direct_intensity",
    "explode",
    "glass",
    "grid",
    "grid_font_size",
    "metalness",
    "modifier_keys",
    "orbit_control",
    "ortho",
    "pan_speed",
    "rotate_speed",
    "roughness",
    "states",
    "studio_4k_env_maps",
    "studio_ao_intensity",
    "studio_background",
    "studio_env_intensity",
    "studio_env_rotation",
    "studio_environment",
    "studio_exposure",
    "studio_shadow_intensity",
    "studio_shadow_softness",
    "studio_texture_mapping",
    "studio_tone_mapping",
    "tab",
    "ticks",
    "tools",
    "transparent",
    "tree_width",
    "up",
    "zebra_color_scheme",
    "zebra_count",
    "zebra_direction",
    "zebra_mapping_mode",
    "zebra_opacity",
    "zoom_speed",
)

# What this host cannot be told, because the webview decides it: the panel's
# geometry is the panel's. Jupyter CadQuery, where a cell asks for a widget of a
# given size, excludes neither.

# The keywords that belong to other hosts. The show signature is the superset of
# every client's, so a key one host owns is a key another has to refuse - and
# refusing it by name is what tells a user their `anchor=` went nowhere instead
# of leaving them to wonder.
#
# `cad_width` and `height` are this surface's own to decide, where a notebook
# cell is told them; `viewer`, `anchor` and `pinning` name a sidecar this host
# does not have.
EXCLUDE_KEYS = ("cad_width", "height", "viewer", "anchor", "pinning")

session = Session(comms)
config = Config(session, WORKSPACE_CONFIG_KEYS, EXCLUDE_KEYS)

set_defaults = config.set_defaults
set_viewer_config = config.set_viewer_config
check_deprecated = config.check_deprecated
validate_tool_args = config.validate_tool_args


# The small entry points keep the port keyword and open the scope so the
# transport can act on it. They wrap rather than nest: the core's calls between
# its own methods go straight to the methods, never back through here.


def status(port=None, debug=False):
    """Get viewer status"""
    session.begin({"port": port})
    try:
        return config.status(debug=debug)
    finally:
        session.clear()


def workspace_config(port=None):
    """Get viewer workspace config"""
    session.begin({"port": port})
    try:
        return config.workspace_config()
    finally:
        session.clear()


def combined_config(port=None):
    """Get combined config from workspace and status"""
    session.begin({"port": port})
    try:
        return config.combined_config()
    finally:
        session.clear()


def get_changed_config(key=None, port=None):
    """Get changed config from workspace and status"""
    session.begin({"port": port})
    try:
        return config.get_changed_config(key=key)
    finally:
        session.clear()


def get_defaults(port=None):
    """Get all defaults"""
    session.begin({"port": port})
    try:
        return config.get_defaults()
    finally:
        session.clear()


def get_default(key, port=None):
    """Get default value for key"""
    session.begin({"port": port})
    try:
        return config.get_default(key)
    finally:
        session.clear()


def preset(key, value, port=None):
    """The default for key, unless a value was given"""
    session.begin({"port": port})
    try:
        return config.preset(key, value)
    finally:
        session.clear()


def reset_defaults(port=None):
    """Reset defaults not given in workspace config"""
    session.begin({"port": port})
    try:
        return config.reset_defaults()
    finally:
        session.clear()
