"""`resolve`: the defaults, the user's file and the command line, in that order."""

import yaml

from ocp_viewer.server.settings import DEFAULTS, resolve, write_config_file


def test_defaults_alone_give_the_renderer_vocabulary():
    config = resolve({})
    # The command line's inversions and splits are undone.
    assert config["glass"] is True
    assert config["tools"] is True
    assert config["ortho"] is True
    assert config["grid"] == [False, False, False]
    for gone in ("no_glass", "no_tools", "perspective", "grid_xy", "grid_xz", "grid_yz"):
        assert gone not in config
    assert config["collapse"] == "leaves"
    assert config["reset_camera"] == "KEEP"
    assert list(config) == sorted(config), "keys are sorted, so two configs diff line by line"


def test_file_overrides_defaults_and_command_line_overrides_file(config_file):
    config_file.write_text(yaml.dump({"theme": "dark", "ticks": 8, "tree_width": 300}))
    config = resolve({"tree_width": 333})
    assert config["theme"] == "dark"  # file
    assert config["ticks"] == 8  # file
    assert config["tree_width"] == 333  # command line over file


def test_a_typed_value_wins_over_the_file_even_when_it_is_the_built_in_default(config_file):
    # `resolve` only sees what the user typed (track_param in __main__ drops
    # click's defaults), so a value equal to the built-in default is still a
    # choice - the regression test_cli guards for --zoom_speed 1.0, at this level.
    config_file.write_text(yaml.dump({"theme": "dark", "zoom_speed": 0.5}))
    config = resolve({"theme": "browser", "zoom_speed": 1})
    assert config["theme"] == "browser"
    assert config["zoom_speed"] == 1


def test_grid_flags_only_turn_planes_on(config_file):
    config_file.write_text(yaml.dump({"grid_xz": True}))
    assert resolve({"grid_yz": True})["grid"] == [False, True, True]
    assert resolve({"grid_xy": True, "grid_xz": True, "grid_yz": True})["grid"] == [True, True, True]


def test_inverted_flags_flip_the_renderer_booleans():
    config = resolve({"no_glass": True, "no_tools": True, "perspective": True})
    assert (config["glass"], config["tools"], config["ortho"]) == (False, False, False)


def test_values_the_file_may_have_written_loosely_are_normalised(config_file):
    config_file.write_text(yaml.dump({"collapse": 1, "reset_camera": "center"}))
    config = resolve({})
    assert config["collapse"] == "1"
    assert config["reset_camera"] == "CENTER"


def test_a_2_9_0_file_without_the_alt_key_gets_one(config_file):
    config_file.write_text(
        yaml.dump({"modifier_keys": {"shift": "shiftKey", "ctrl": "ctrlKey", "meta": "metaKey"}})
    )
    assert resolve({})["modifier_keys"]["alt"] == "altKey"


def test_server_parameters_never_reach_the_viewer_config():
    config = resolve({"port": 4242, "host": "0.0.0.0", "create_configfile": True, "max_reconnect_attempts": 7})
    for key in ("port", "host", "create_configfile", "max_reconnect_attempts"):
        assert key not in config


def test_write_config_file_round_trips_the_defaults(config_file):
    assert write_config_file() == config_file
    assert yaml.safe_load(config_file.read_text()) == DEFAULTS
    assert resolve({}) == resolve({}) and "theme" in resolve({})  # a written file changes nothing
