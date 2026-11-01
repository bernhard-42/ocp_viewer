"""The server's settings: the defaults, the config file, and the CLI on top.

Named `settings.py` rather than `config.py` because `config.py` in a host of
the core means the config keys and the semantics over them. These are the
values the server starts with; the VS Code extension's equivalents are its
workspace settings, read by the editor.

Three sources in order - these defaults, then `~/.ocpvscode_standalone` if the
user wrote one, then whatever the command line set. The last of those is the
awkward one: click gives a value for every option whether the user typed it or
not, so "was this set" is answered by comparing against the default rather than
by asking click.

The names here are the viewer's own vocabulary, which is not quite the
renderer's: `no_glass` and `no_tools` are inverted flags because a command line
reads better that way, `perspective` is the opposite of `ortho`, and the three
`grid_*` flags become one list. Translating them is this module's job, so that
nothing downstream has to know the command line existed.
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

import sys
from pathlib import Path

import yaml

# The file keeps its name. A user who has one should not have to move it
# because the package it belongs to was renamed.
CONFIG_FILE = Path.home() / ".ocpvscode_standalone"

DEFAULT_MODIFIER_KEYS = {
    "macOS": {"shift": "shiftKey", "ctrl": "ctrlKey", "meta": "metaKey", "alt": "altKey"},
    "default": {"shift": "shiftKey", "ctrl": "ctrlKey", "meta": "altKey", "alt": "metaKey"},
}


def resolve_modifier_keys(value, platform=None):
    """The stored map for this machine's operating system.

    The stored value is one map per platform, `{"macOS": ..., "default": ...}`,
    so that whoever opens the file sees which platform gets what - the shape
    build123d Studio and the VS Code extension store. `meta` rotates, hides
    and isolates, and `metaKey` is Cmd on macOS but the Win/Super key on
    Windows and Linux, which the desktop takes for itself (the Start menu,
    window snapping, moving windows) - those chords never reach the page, so
    there `meta` and `alt` swap physical keys. A flat map, the shape of a file
    written by an earlier release, is taken as it is on every platform.
    """
    if not isinstance(value, dict) or ("default" not in value and "macOS" not in value):
        return value
    platform = sys.platform if platform is None else platform
    if platform == "darwin" and value.get("macOS") is not None:
        return dict(value["macOS"])
    return dict(value.get("default", value.get("macOS")))


def upgrade_modifier_keys(value, platform=None):
    """A flat map from an older file, lifted into the per-platform shape.

    The flat map is what the user chose on the machine that wrote the file,
    so it goes under that machine's platform; the other platform gets the
    shipped default. Written back that way, the file then works on both. A
    value already in the per-platform shape is returned as it is.
    """
    if not isinstance(value, dict) or "default" in value or "macOS" in value:
        return value
    platform = sys.platform if platform is None else platform
    upgraded = {key: dict(keys) for key, keys in DEFAULT_MODIFIER_KEYS.items()}
    upgraded["macOS" if platform == "darwin" else "default"] = dict(value)
    return upgraded


DEFAULTS = {
    "debug": False,
    "no_glass": False,
    "no_tools": False,
    "tree_width": 240,
    "theme": "browser",
    "control": "trackball",
    # Rotate around and zoom towards the point under the cursor, for trackball
    # and orbit control. False rotates and zooms around the target.
    "cursor_pivot": True,
    "modifier_keys": dict(DEFAULT_MODIFIER_KEYS),
    "new_tree_behavior": True,
    "pan_speed": 1,
    "rotate_speed": 1,
    "zoom_speed": 1,
    "axes": False,
    "axes0": True,
    "grid_xy": False,
    "grid_xz": False,
    "grid_yz": False,
    "perspective": False,
    "transparent": False,
    "black_edges": False,
    # The name, not the "1"/"E"/"C"/"R" shorthand it used to be. Both reach the
    # same Collapse.LEAVES through the core's mapping, so nothing behaves
    # differently and an existing config file keeps working - but two
    # vocabularies for one setting is exactly what stops a value learnt in one
    # viewer meaning anything in the next. This host's own --collapse help has
    # documented the names all along.
    "collapse": "leaves",
    "reset_camera": "KEEP",
    "up": "Z",
    "ticks": 5,
    "center_grid": False,
    "grid_font_size": 12,
    "default_opacity": 0.5,
    "explode": False,
    "default_edgecolor": "#707070",
    "default_color": "#e8b024",
    "default_thickedgecolor": "MediumOrchid",
    "default_facecolor": "Violet",
    "default_vertexcolor": "MediumOrchid",
    "angular_tolerance": 0.2,
    "deviation": 0.1,
    # 1 rather than 1.0, which is what the other three hosts declare. The same
    # number either way; written the same way so a comparison across the four
    # answers is a comparison of values and not of literals.
    "ambient_intensity": 1,
    "direct_intensity": 1.1,
    "metalness": 0.3,
    "roughness": 0.65,
    # ocp-tessellate's naming of repeated objects, read by Python's show and
    # never by the page. True numbers them from 0 like Python indices; False
    # restores the former names, which are the tree paths animations, states
    # and selections address.
    "python_enumeration": True,
}

# Not settings: where to listen, and how the page should behave if the server
# goes away. They are read straight off the params and never reach the viewer.
NOT_VIEWER_SETTINGS = ("port", "host", "create_configfile", "max_reconnect_attempts")


def write_config_file():
    """Write the defaults to the config file, for a user to edit."""
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        f.write(yaml.dump(DEFAULTS))
    return CONFIG_FILE


def _from_file():
    if not CONFIG_FILE.exists():
        return {}
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def resolve(params):
    """The viewer config, from the defaults, the file and the command line.

    Returns the config the viewer and the page are given - in the renderer's
    vocabulary, with the command line's inversions already undone.
    """
    settings = {**DEFAULTS, **_from_file()}

    # A grid flag on the command line only ever turns a plane on: the three
    # options are `--grid-xy` and friends, and there is no `--no-grid-xy`.
    grid = [settings["grid_xy"], settings["grid_xz"], settings["grid_yz"]]
    for key, value in params.items():
        if key in NOT_VIEWER_SETTINGS:
            continue
        if value == settings.get(key):
            continue
        if key in ("grid_xy", "grid_xz", "grid_yz"):
            grid[("grid_xy", "grid_xz", "grid_yz").index(key)] = True
        else:
            settings[key] = value

    config = {
        "grid": grid,
        # The viewer takes the mode as a string, and the config file may have
        # written it as an integer.
        "collapse": str(settings["collapse"]),
        # Inverted on the command line, because a flag that turns something off
        # reads better than one that takes a boolean.
        "glass": not settings["no_glass"],
        "tools": not settings["no_tools"],
        "ortho": not settings["perspective"],
        # str() because the settings dict holds every type the config file
        # may carry, and a camera mode written without quotes arrives as
        # something without .upper().
        "reset_camera": str(settings["reset_camera"]).upper(),
    }
    for key, value in settings.items():
        if key not in ("grid_xy", "grid_xz", "grid_yz", *config, "no_glass",
                       "no_tools", "perspective"):
            config[key] = value

    # The file keeps one map per platform; the viewer gets this platform's. A
    # flat map from an older file is this platform's choice, lifted first.
    keys = resolve_modifier_keys(upgrade_modifier_keys(config.get("modifier_keys")))
    # For compatibility with 2.9.0, whose config files have no alt key.
    if isinstance(keys, dict) and keys.get("alt") is None:
        keys["alt"] = "altKey"
    config["modifier_keys"] = keys

    return dict(sorted(config.items()))
