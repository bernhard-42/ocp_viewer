"""The command line: `python -m ocp_viewer`.

Every option is a viewer setting, and click hands us a value for all of them
whether the user typed one or not - so `track_param` records which were
actually set, and only those override the config file. That is the whole reason
the callback exists.
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

import click
import yaml

from . import serve
from .config import DEFAULTS, write_config_file


def represent_list(dumper, data):
    """Write a YAML list on one line, so a config file stays readable."""
    return dumper.represent_sequence("tag:yaml.org,2002:seq", data, flow_style=True)


yaml.add_representer(list, represent_list)


def track_param(ctx, param, value):
    """Record the options the user actually gave.

    click cannot be asked "was this set", and a default handed on as though it
    were a choice would override the config file with the built-in value. The
    three that are always recorded are not settings: they say where to listen
    and how loudly.
    """
    if not hasattr(ctx, "params_set"):
        ctx.params_set = {}
    if value != param.default or param.name in ["port", "host", "debug"]:
        ctx.params_set[param.name] = value
    return value


@click.command()
@click.option(
    "--create_configfile",
    is_flag=True,
    help="Create the config file .ocpvscode_standalone in the home directory",
    callback=track_param,
)
@click.option(
    "--host",
    default="127.0.0.1",
    help="The host to start OCP CAD with",
    callback=track_param,
)
@click.option(
    "--port",
    default=3939,
    help="The port to start OCP CAD with",
    callback=track_param,
)
@click.option(
    "--debug",
    is_flag=True,
    help="Show debugging information",
    callback=track_param,
)
@click.option(
    "--timeit",
    is_flag=True,
    help="Show timing information",
    callback=track_param,
)
@click.option(
    "--tree_width",
    type=click.INT,
    default=None,
    help=f"OCP CAD Viewer navigation tree width (default: {DEFAULTS['tree_width']})",
    callback=track_param,
)
@click.option(
    "--no_glass",
    is_flag=True,
    help="Do not use glass mode with transparent navigation tree",
    callback=track_param,
)
@click.option(
    "--theme",
    type=click.STRING,
    default=None,
    help=f"Use theme 'light', 'dark', or 'browser' (default: {DEFAULTS['theme']!r})",
    callback=track_param,
)
@click.option(
    "--no_tools",
    is_flag=True,
    help="Do not show toolbar",
    callback=track_param,
)
@click.option(
    "--control",
    type=click.STRING,
    default=None,
    help=f"Use control mode 'orbit' or 'trackball' (default: {DEFAULTS['control']!r})",
    callback=track_param,
)
@click.option(
    "--reset_camera",
    type=click.STRING,
    default=None,
    help=f"Set camera behavior to 'reset', 'keep' or 'center' (default: {DEFAULTS['reset_camera']!r})",
    callback=track_param,
)
@click.option(
    "--up",
    type=click.STRING,
    default=None,
    help=f"Provides up direction, 'Z', 'Y' or 'L' (legacy) (default: {DEFAULTS['up']!r})",
    callback=track_param,
)
@click.option(
    "--rotate_speed",
    type=click.FLOAT,
    default=None,
    help=f"Rotation speed (default: {DEFAULTS['rotate_speed']})",
    callback=track_param,
)
@click.option(
    "--zoom_speed",
    type=click.FLOAT,
    default=None,
    help=f"Zoom speed (default: {DEFAULTS['zoom_speed']})",
    callback=track_param,
)
@click.option(
    "--pan_speed",
    type=click.FLOAT,
    default=None,
    help=f"Pan speed (default: {DEFAULTS['pan_speed']})",
    callback=track_param,
)
@click.option(
    "--axes",
    is_flag=True,
    help="Show axes",
    callback=track_param,
)
@click.option(
    "--axes0",
    is_flag=True,
    help="Show axes at the origin (0, 0, 0)",
    callback=track_param,
)
@click.option(
    "--black_edges",
    is_flag=True,
    help="Show edges in black",
    callback=track_param,
)
@click.option(
    "--grid_xy",
    is_flag=True,
    help="Show grid on XY plane",
    callback=track_param,
)
@click.option(
    "--grid_yz",
    is_flag=True,
    help="Show grid on YZ plane",
    callback=track_param,
)
@click.option(
    "--grid_xz",
    is_flag=True,
    help="Show grid on XZ plane",
    callback=track_param,
)
@click.option(
    "--center_grid",
    is_flag=True,
    help="Show grid planes crossing at center of object or global origin (default: False)",
    callback=track_param,
)
@click.option(
    "--grid_font_size",
    type=click.INT,
    default=None,
    help=f"Size of grid's axis label font (default: {DEFAULTS['grid_font_size']})",
    callback=track_param,
)
@click.option(
    "--collapse",
    type=click.STRING,
    default=None,
    help=(
        "leaves: collapse all single-leaf nodes, all: collapse all nodes, "
        "none: expand all nodes, root: expand root only "
        f"(default: {DEFAULTS['collapse']!r})"
    ),
    callback=track_param,
)
@click.option(
    "--perspective",
    is_flag=True,
    help="Use perspective camera",
    callback=track_param,
)
@click.option(
    "--ticks",
    type=click.INT,
    default=None,
    help=f"Default number of ticks (default: {DEFAULTS['ticks']})",
    callback=track_param,
)
@click.option(
    "--transparent",
    is_flag=True,
    help="Show objects transparent",
    callback=track_param,
)
@click.option(
    "--default_opacity",
    type=click.FLOAT,
    default=None,
    help=f"Default opacity for transparent objects (default: {DEFAULTS['default_opacity']})",
    callback=track_param,
)
@click.option(
    "--explode",
    is_flag=True,
    help="Turn explode mode on",
    callback=track_param,
)
@click.option(
    "--angular_tolerance",
    type=click.FLOAT,
    default=None,
    help=f"Angular tolerance for tessellation algorithm (default: {DEFAULTS['angular_tolerance']})",
    callback=track_param,
)
@click.option(
    "--deviation",
    type=click.FLOAT,
    default=None,
    help=f"Deviation for tessellation algorithm (default: {DEFAULTS['deviation']})",
    callback=track_param,
)
@click.option(
    "--default_color",
    type=click.STRING,
    default=None,
    help=f"Default shape color, CSS3 color names are allowed (default: {DEFAULTS['default_color']})",
    callback=track_param,
)
@click.option(
    "--default_edgecolor",
    type=click.STRING,
    default=None,
    help=f"Default color of the edges of shapes, CSS3 color names are allowed (default: {DEFAULTS['default_edgecolor']})",
    callback=track_param,
)
@click.option(
    "--default_thickedgecolor",
    type=click.STRING,
    default=None,
    help=f"Default color of thick edges, CSS3 color names are allowed (default: {DEFAULTS['default_thickedgecolor']})",
    callback=track_param,
)
@click.option(
    "--default_facecolor",
    type=click.STRING,
    default=None,
    help=f"Default color of faces, CSS3 color names are allowed (default: {DEFAULTS['default_facecolor']})",
    callback=track_param,
)
@click.option(
    "--default_vertexcolor",
    type=click.STRING,
    default=None,
    help=f"Default color of vertices, CSS3 color names are allowed (default: {DEFAULTS['default_vertexcolor']})",
    callback=track_param,
)
@click.option(
    "--ambient_intensity",
    type=click.FLOAT,
    default=None,
    help=f"Intensity of ambient light (default: {DEFAULTS['ambient_intensity']})",
    callback=track_param,
)
@click.option(
    "--direct_intensity",
    type=click.FLOAT,
    default=None,
    help=f"Intensity of direct light (default: {DEFAULTS['direct_intensity']})",
    callback=track_param,
)
@click.option(
    "--metalness",
    type=click.FLOAT,
    default=None,
    help=f"Metalness property of material (default: {DEFAULTS['metalness']})",
    callback=track_param,
)
@click.option(
    "--roughness",
    type=click.FLOAT,
    default=None,
    help=f"Roughness property of material (default: {DEFAULTS['roughness']})",
    callback=track_param,
)
@click.option(
    "--max_reconnect_attempts",
    default=300,
    help="Maximum number of attempts to reconnect to the viewer server in standalone mode. Use -1 for infinite attempts (default: 300)",
    callback=track_param,
)
@click.pass_context
def main(ctx, **kwargs):
    """Write a config file, or run the viewer.

    `ctx.params_set` rather than `kwargs`: it holds the options the user
    actually gave, and the config file fills in the rest.
    """

    if kwargs.get("create_configfile"):
        print(f"Created config file {write_config_file()}")
        return

    serve(ctx.params_set)


if __name__ == "__main__":
    main()
