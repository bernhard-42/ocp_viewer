"""The show family, bound to this host's viewer.

The pipeline is `ocp_viewer_core.show.Viewer`; what is here is the one Viewer
this process shows through and the names bound off it. Bound methods and
nothing else - `show` carries 84 keywords, and a wrapper would have to restate
every one to keep hover and completion.

The same file, the same names and the same reasoning as ocp_vscode's show.py.
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

from ocp_viewer_core.show import Viewer, ignore_camera_warnings, none_filter

from ocp_viewer.config import config

__all__ = [
    "get_colormap",
    "get_last_paths",
    "ignore_camera_warnings",
    "none_filter",
    "push_object",
    "remove_object",
    "reset_show",
    "save_screenshot",
    "set_colormap",
    "show",
    "show_all",
    "show_clear",
    "show_object",
    "show_objects",
    "unset_colormap",
]

# `None` is the handle type: the browser hands nothing back, so `show` returns
# None here.
viewer = Viewer[None](config)

show = viewer.show
show_object = viewer.show_object
show_objects = viewer.show_objects
show_all = viewer.show_all
show_clear = viewer.show_clear
push_object = viewer.push_object
remove_object = viewer.remove_object
reset_show = viewer.reset_show
save_screenshot = viewer.save_screenshot

get_colormap = viewer.get_colormap
set_colormap = viewer.set_colormap
unset_colormap = viewer.unset_colormap
get_last_paths = viewer.get_last_paths
