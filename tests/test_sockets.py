"""The one websocket and the six kinds of message on it, against the real server.

Every test runs the server in-process (see conftest.py) and speaks to it as the
two real clients do: Python with a connection per message, the browser with one
it keeps and registers with `L`.
"""

import base64
import time

import orjson
import pytest
from ocp_viewer_core.logo import logo

PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 16


def status_update(text):
    return "U:" + orjson.dumps({"command": "status", "text": text}).decode("utf-8")


def nothing_arrives(ws, seconds=0.3):
    with pytest.raises(TimeoutError):
        ws.recv(timeout=seconds)


# --- commands: the two questions, and the two things done to a viewer ------


def test_config_answers_the_settings_and_whether_the_splash_is_up(standalone):
    r = standalone(theme="dark", no_glass=True)
    config = r.python("C", "config", reply=True)
    assert config["theme"] == "dark"
    assert config["glass"] is False
    assert config["_splash"] is True

    with r.browser():
        r.python("D", {"type": "data", "model": "anything"})
        r.wait(lambda v: v.splash is False)
    assert r.python("C", "config", reply=True)["_splash"] is False


def test_status_answers_what_the_browser_last_reported(standalone):
    r = standalone()
    assert r.python("C", "status", reply=True) == {"command": "status", "text": {}}

    with r.browser() as browser:
        browser.send(status_update({"axes": True, "grid": [True, False, False]}))
        r.wait(lambda v: v.status.get("axes") is True)
        browser.send(status_update({"grid": [True, True, False]}))
        r.wait(lambda v: v.status.get("grid") == [True, True, False])

    assert r.python("C", "status", reply=True) == {
        "command": "status",
        "text": {"axes": True, "grid": [True, True, False]},
    }


@pytest.mark.parametrize("kind", ["screenshot", "set_relative_time"])
def test_the_two_commands_done_to_a_viewer_are_relayed_without_a_reply(standalone, kind):
    r = standalone()
    with r.browser() as browser:
        command = {"type": kind, "filename": "x.png", "time": 0.5}
        r.python("C", command)
        assert orjson.loads(browser.recv(timeout=5)) == command


def test_an_unknown_command_reaches_nobody(standalone):
    r = standalone()
    with r.browser() as browser:
        r.python("C", {"type": "reboot"})
        nothing_arrives(browser)


# --- models and configs: relayed exactly as they arrived ------------------


def test_a_model_and_a_config_reach_the_browser_byte_for_byte(standalone):
    r = standalone()
    model = orjson.dumps({"type": "data", "blob": "x" * 100_000, "nested": {"a": [1, 2.5, None]}})
    config = orjson.dumps({"type": "ui", "config": {"tab": "studio", "glass": False}})
    with r.browser() as browser:
        r.python("D", model)
        r.python("S", config)
        assert browser.recv(timeout=5) == model.decode("utf-8")
        assert browser.recv(timeout=5) == config.decode("utf-8")


def test_without_a_browser_a_model_is_dropped_and_said_so(standalone, capsys):
    r = standalone()
    r.python("D", {"type": "data"})
    r.python("S", {"type": "ui"})
    time.sleep(0.2)
    assert capsys.readouterr().out.count("No browser registered") == 2
    assert r.viewer.splash is True, "a model nobody saw does not take the splash down"


def test_the_latest_registered_page_is_the_browser(standalone):
    r = standalone()
    with r.browser() as first:
        registered_first = r.viewer.browser
        with r.browser() as second:
            r.wait(lambda v: v.browser is not registered_first)
            r.python("D", {"type": "data", "n": 2})
            assert orjson.loads(second.recv(timeout=5)) == {"type": "data", "n": 2}
            nothing_arrives(first)


def test_a_browser_that_went_away_is_forgotten(standalone, capsys):
    r = standalone()
    browser = r.browser()
    browser.close()
    r.wait(lambda v: v.browser is None)
    r.python("D", {"type": "data"})
    time.sleep(0.2)
    assert "No browser registered" in capsys.readouterr().out


def test_a_page_that_reconnects_is_served_again(standalone):
    r = standalone()
    with r.browser() as browser:
        browser.close()
    r.wait(lambda v: v.browser is None)
    with r.browser() as again:
        r.python("D", {"type": "data", "again": True})
        assert orjson.loads(again.recv(timeout=5)) == {"type": "data", "again": True}


# --- the browser's reports ------------------------------------------------


def test_a_screenshot_from_the_browser_is_written_where_it_asked(standalone, tmp_path):
    r = standalone()
    target = tmp_path / "shot.png"
    data_url = "data:image/png;base64," + base64.b64encode(PNG).decode("ascii")
    with r.browser() as browser:
        browser.send(
            "U:"
            + orjson.dumps(
                {"command": "screenshot", "text": {"data": data_url, "filename": str(target)}}
            ).decode("utf-8")
        )
        deadline = time.time() + 5
        while not target.exists():
            assert time.time() < deadline
            time.sleep(0.01)
    assert target.read_bytes() == PNG


def test_log_and_started_are_printed_in_debug_only(standalone, capsys):
    quiet = standalone()
    with quiet.browser() as browser:
        browser.send("U:" + orjson.dumps({"command": "log", "text": "hello"}).decode())
        browser.send("U:" + orjson.dumps({"command": "started", "text": ""}).decode())
        time.sleep(0.2)
    assert "hello" not in capsys.readouterr().out

    loud = standalone(debug=True)
    with loud.browser() as browser:
        browser.send("U:" + orjson.dumps({"command": "log", "text": "hello"}).decode())
        browser.send("U:" + orjson.dumps({"command": "started", "text": ""}).decode())
        time.sleep(0.2)
    out = capsys.readouterr().out
    assert "Debug: [log] hello" in out
    assert "Debug: Viewer has started" in out


# --- the backend: it answers on the socket the question came in on ---------


def test_the_splash_is_measurable_before_any_model_was_shown(standalone):
    r = standalone()
    with r.browser() as browser:
        browser.send(
            status_update(
                {
                    "activeTool": "PropertiesMeasurement",
                    "selectedShapeIDs": ["/Group/OCP/faces/faces_0", False],
                }
            )
        )
        answer = browser.recv(timeout=10)
        assert isinstance(answer, str), "a text frame: the page reads text, not a Blob"
        response = orjson.loads(answer)
    assert response["type"] == "backend_response"
    assert response["subtype"] == "tool_response"
    assert response["tool_type"] == "PropertiesMeasurement"


def test_distance_between_the_two_logo_shapes(standalone):
    r = standalone()
    with r.browser() as browser:
        browser.send(
            status_update(
                {
                    "activeTool": "DistanceMeasurement",
                    "selectedShapeIDs": ["/Group/OCP", "/Group/Eye", False],
                }
            )
        )
        response = orjson.loads(browser.recv(timeout=10))
    assert response["tool_type"] == "DistanceMeasurement"


def test_a_change_with_no_usable_selection_gets_no_answer(standalone):
    r = standalone()
    with r.browser() as browser:
        browser.send(status_update({"activeTool": "PropertiesMeasurement"}))
        nothing_arrives(browser)
        browser.send(status_update({"activeTool": "None"}))
        browser.send(status_update({"selectedShapeIDs": ["/Group/OCP/faces/faces_0", False]}))
        nothing_arrives(browser)


def test_a_model_sent_to_the_backend_is_acknowledged_and_replaces_the_splash(standalone):
    r = standalone()
    assert "/Group/OCP" in r.viewer.backend.model
    box = {
        "id": "/Group",
        "parts": [
            {
                "id": "/Group/Box",
                "shape": logo["parts"][0]["shape"],
                "loc": logo["parts"][0]["loc"],
            }
        ],
    }
    assert r.python("B", {"model": box}, reply=True) == {"ok": True}
    assert "/Group/Box" in r.viewer.backend.model
    assert "/Group/Eye" not in r.viewer.backend.model


# --- several viewers in one process ---------------------------------------


def test_two_viewers_on_two_ports_share_nothing(standalone, monkeypatch):
    # The stub answers `workspace_config` from a canned dict while the variable
    # is set; this test wants the real answer from each real server.
    monkeypatch.delenv("OCP_VIEWER_PYTEST", raising=False)
    from ocp_viewer import workspace_config

    a = standalone(theme="dark")
    b = standalone(theme="light")
    assert a.port != b.port
    assert a.viewer is not b.viewer
    assert a.viewer.backend is not b.viewer.backend

    # Each answers its own settings, addressed by port, through the real client.
    assert workspace_config(port=a.port)["theme"] == "dark"
    assert workspace_config(port=b.port)["theme"] == "light"

    with a.browser() as page_a, b.browser() as page_b:
        # A model to one reaches only that one's page, and only that one's splash goes down.
        a.python("D", {"type": "data", "to": "a"})
        assert orjson.loads(page_a.recv(timeout=5)) == {"type": "data", "to": "a"}
        nothing_arrives(page_b)
        a.wait(lambda v: v.splash is False)
        assert b.viewer.splash is True

        # A report from one page lands in that viewer's status alone.
        page_b.send(status_update({"axes": True}))
        b.wait(lambda v: v.status.get("axes") is True)
        assert a.viewer.status == {}
        assert a.python("C", "status", reply=True)["text"] == {}
        assert b.python("C", "status", reply=True)["text"] == {"axes": True}

        # The backends are separate: a model loaded into one is unknown to the other.
        box = {"id": "/Group", "parts": [{"id": "/Group/Box", "shape": logo["parts"][0]["shape"], "loc": None}]}
        assert b.python("B", {"model": box}, reply=True) == {"ok": True}
        assert "/Group/Box" in b.viewer.backend.model
        assert "/Group/Box" not in a.viewer.backend.model
        assert "/Group/OCP" in a.viewer.backend.model


# --- the server's stored settings reach a client's show ---------------------


def test_timeit_and_debug_from_the_command_line_reach_a_client(standalone, monkeypatch):
    # Level 1 of a client's config is this server's workspace config; the core's
    # built-in False for these two used to be applied on top of it, so
    # `--timeit` was stored, reported, and never seen by a show.
    monkeypatch.delenv("OCP_VIEWER_PYTEST", raising=False)
    from ocp_viewer import get_default

    r = standalone(timeit=True, debug=True)
    assert get_default("timeit", port=r.port) is True
    assert get_default("debug", port=r.port) is True
    assert get_default("timeit", port=standalone().port) is False
