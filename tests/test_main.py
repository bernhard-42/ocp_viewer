"""The command line: only what the user typed reaches the server."""

from click.testing import CliRunner

from ocp_viewer import __main__ as cli
from ocp_viewer.server.settings import DEFAULTS


def invoke(monkeypatch, *args):
    seen = {}
    monkeypatch.setattr(cli, "serve", lambda params: seen.update(params))
    result = CliRunner().invoke(cli.main, list(args))
    assert result.exit_code == 0, result.output
    return seen


def test_defaults_are_not_choices(monkeypatch):
    # The three that say where and how loudly are always passed on.
    assert invoke(monkeypatch) == {"host": "127.0.0.1", "port": 3939, "debug": False}


def test_what_the_user_typed_is_passed_on_with_its_type(monkeypatch):
    seen = invoke(monkeypatch, "--theme", "dark", "--zoom_speed", "1.0", "--grid_xy", "--ticks", "7", "--no_glass")
    assert seen == {
        "host": "127.0.0.1",
        "port": 3939,
        "debug": False,
        "theme": "dark",
        "zoom_speed": 1.0,
        "grid_xy": True,
        "ticks": 7,
        "no_glass": True,
    }


def test_create_configfile_writes_the_defaults_and_does_not_serve(monkeypatch, config_file):
    served = []
    monkeypatch.setattr(cli, "serve", served.append)
    result = CliRunner().invoke(cli.main, ["--create_configfile"])
    assert result.exit_code == 0, result.output
    assert f"Created config file {config_file}" in result.output
    assert config_file.exists()
    assert served == []


def test_every_viewer_option_is_a_setting():
    # `timeit` is a client-side setting the server only stores (see
    # test_sockets: it reaches a client's show through the workspace config);
    # `debug` is both a server option and a viewer setting. Two settings have
    # no option: the keymap, which is a dict, and new_tree_behavior, which is
    # only ever set in the file.
    server_options = {"host", "port", "timeit", "create_configfile", "max_reconnect_attempts"}
    options = {p.name for p in cli.main.params} - server_options
    assert options == set(DEFAULTS) - {"modifier_keys", "new_tree_behavior"}, (
        "an option without a default, or a default without an option"
    )
