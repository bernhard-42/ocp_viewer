"""Which config keys this host stores, and which it may not be told.

The two lists every host of the core supplies. They are the same as
ocp_vscode's, and deliberately so: both serve a three-cad-viewer of the same
version, so the keys its status reports are the same keys.

`cad_width` and `height` are excluded for the same reason as there - the page
sizes itself to the window it is in, and a script asking for a width would be
asking the browser to resize.
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

EXCLUDE_KEYS = ("cad_width", "height")
