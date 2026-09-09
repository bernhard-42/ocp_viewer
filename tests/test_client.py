"""The client half: names bound off one Viewer and one Config, and nothing else."""

import importlib

import pytest

import ocp_viewer

# The package re-exports the `comms` instance under the module's own name, so
# the module is reached by import, not by attribute.
comms_module = importlib.import_module("ocp_viewer.comms")
from ocp_viewer.animation import Animation
from ocp_viewer.config import config, session
from ocp_viewer.show import viewer


@pytest.fixture(autouse=True)
def restore_client_port():
    c = comms_module.comms
    saved = (c._port, c.host, c._resolved)
    yield
    c._port, c.host, c._resolved = saved


def test_every_exported_name_resolves():
    for name in ocp_viewer.__all__:
        getattr(ocp_viewer, name)


def test_the_star_import_is_exactly_all():
    namespace = {}
    exec("from ocp_viewer import *", namespace)  # noqa: S102 - the star import is what is under test
    assert {n for n in namespace if not n.startswith("__")} == set(ocp_viewer.__all__)


def test_the_show_family_is_bound_to_the_one_viewer():
    for name in ("show", "show_object", "show_objects", "show_all", "show_clear", "save_screenshot"):
        assert getattr(ocp_viewer, name).__self__ is viewer
    assert Animation is ocp_viewer.Animation
    assert viewer.config is config
    assert config.session is session
    assert session.comms is comms_module.comms


def test_the_setters_are_bound_to_the_one_config_and_the_port_scoped_reads_wrap_it():
    for name in ("set_defaults", "set_viewer_config"):
        assert getattr(ocp_viewer, name).__self__ is config
    # These take a `port` and open the session's keyword scope around the
    # call, so they are functions of this package rather than bound methods.
    for name in ("get_defaults", "get_default", "reset_defaults", "status", "workspace_config", "combined_config"):
        assert getattr(ocp_viewer, name).__module__ == "ocp_viewer.config"
    assert isinstance(ocp_viewer.get_defaults(port=4242), dict)


def test_set_port_pins_the_client_and_skips_discovery():
    ocp_viewer.set_port(4242, "10.0.0.7")
    assert ocp_viewer.get_port() == 4242
    assert comms_module.comms.host == "10.0.0.7"
    assert comms_module.comms._resolved is True
