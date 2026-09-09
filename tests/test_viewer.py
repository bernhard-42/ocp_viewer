"""`Viewer`: what a running viewer knows, and how it keeps it."""

import yaml

from ocp_viewer.server.viewer import Viewer


def test_record_keeps_the_picture_and_returns_only_what_changed():
    viewer = Viewer({})
    assert viewer.record({"axes": True, "grid": [True, False, False]}) == {
        "axes": True,
        "grid": [True, False, False],
    }
    assert viewer.record({"axes": True, "grid": [True, True, False]}) == {"grid": [True, True, False]}
    assert viewer.record({"axes": True, "grid": [True, True, False]}) == {}
    assert viewer.status == {"axes": True, "grid": [True, True, False]}


def test_reconfigure_rereads_the_file_and_says_whether_the_splash_is_up(config_file):
    viewer = Viewer({"port": 3939})
    assert viewer.config["theme"] == "browser"
    config_file.write_text(yaml.dump({"theme": "dark"}))
    config = viewer.reconfigure()
    assert config["theme"] == "dark"
    assert config["_splash"] is True
    viewer.splash = False
    assert viewer.reconfigure()["_splash"] is False


def test_server_parameters_are_read_off_the_params():
    viewer = Viewer({"host": "0.0.0.0", "port": 4242, "debug": True, "max_reconnect_attempts": -1})
    assert (viewer.host, viewer.port, viewer.debug, viewer.max_reconnect_attempts) == (
        "0.0.0.0",
        4242,
        True,
        -1,
    )
    defaults = Viewer({})
    assert (defaults.host, defaults.port, defaults.debug, defaults.max_reconnect_attempts) == (
        "127.0.0.1",
        3939,
        False,
        None,
    )


def test_log_prints_only_in_debug(capsys):
    Viewer({}).log("quiet")
    Viewer({"debug": True}).log("loud", 1)
    assert capsys.readouterr().out == "Debug: loud 1\n"
