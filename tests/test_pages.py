"""`respond`: the page, the files it loads, the redirect - and nothing else."""

import json
import re

import pytest
from websockets.datastructures import Headers
from websockets.http11 import Request

from ocp_viewer.server import pages
from ocp_viewer.server.viewer import Viewer


def request(path, **headers):
    return Request(path, Headers(list({"Host": "127.0.0.1:3939", **headers}.items())))


def rendered(viewer, **headers):
    response = pages.respond(viewer, request("/viewer", **headers))
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "text/html; charset=utf-8"
    return response.body.decode("utf-8")


def test_a_websocket_upgrade_is_not_answered_here():
    assert pages.respond(Viewer({}), request("/", Upgrade="websocket")) is None


def test_root_redirects_to_the_page():
    response = pages.respond(Viewer({}), request("/"))
    assert (response.status_code, response.headers["Location"]) == (302, "/viewer")


def test_the_page_carries_the_settings_as_json_literals(config_file):
    viewer = Viewer({"theme": "dark", "tree_width": 333, "no_glass": True, "no_tools": True, "up": "Y", "control": "orbit"})
    page = rendered(viewer)
    assert 'theme: "dark"' in page
    assert "treeWidth: 333" in page
    assert "glass: false" in page
    assert "tools: false" in page
    assert 'up: "Y"' in page
    assert 'control: "orbit"' in page
    keymap = re.search(r"keymap: (\{.*\})", page).group(1)
    assert json.loads(keymap) == viewer.config["modifier_keys"]
    assert "$" not in page, "every placeholder was filled"


def test_the_page_dials_back_where_the_browser_reached_the_server():
    assert 'new Comms("cad.local", "8080", undefined)' in rendered(Viewer({}), Host="cad.local:8080")
    # Behind a proxy or on port 80 the Host header has no port; comms.js reads
    # an empty port as the scheme's default.
    assert 'new Comms("cad.local", "", undefined)' in rendered(Viewer({}), Host="cad.local")


def test_the_reconnect_limit_is_rendered_when_given_and_left_to_the_page_otherwise():
    assert 'new Comms("127.0.0.1", "3939", 7)' in rendered(Viewer({"max_reconnect_attempts": 7}))
    assert 'new Comms("127.0.0.1", "3939", -1)' in rendered(Viewer({"max_reconnect_attempts": -1}))
    assert 'new Comms("127.0.0.1", "3939", undefined)' in rendered(Viewer({}))


def test_a_query_string_does_not_change_the_route():
    assert pages.respond(Viewer({}), request("/viewer?x=1")).status_code == 200


@pytest.mark.parametrize(
    "name, content_type, start",
    [
        ("js/comms.js", "text/javascript", b"function handleMessage"),
        ("js/ocp-viewer-core/index.js", "text/javascript", None),
        ("js/three-cad-viewer.esm.js", "text/javascript", None),
        ("css/three-cad-viewer.css", "text/css", None),
        ("icon/ocp-eye.png", "image/png", b"\x89PNG"),
    ],
)
def test_the_files_the_page_loads_are_served_with_their_types(name, content_type, start):
    response = pages.respond(Viewer({}), request(f"/static/{name}"))
    assert response.status_code == 200
    assert response.headers["Content-Type"] == content_type
    assert response.headers["Content-Length"] == str(len(response.body))
    assert response.headers["Cache-Control"] == "no-cache"
    assert response.body == (pages.STATIC / name).read_bytes()
    if start is not None:
        assert response.body.startswith(start)


@pytest.mark.parametrize(
    "path",
    ["/static/../pyproject.toml", "/static/../../README.md", "/static/js/missing.js", "/static/", "/nope", "/viewer/extra"],
)
def test_anything_else_is_not_found(path):
    response = pages.respond(Viewer({}), request(path))
    assert response.status_code == 404
    assert response.headers["Connection"] == "close"


def test_a_placeholder_the_page_names_and_the_server_does_not_fill_is_an_error(monkeypatch, tmp_path):
    broken = tmp_path / "viewer.html"
    broken.write_text("<script>const x = $no_such_value;</script>")
    monkeypatch.setattr(pages, "TEMPLATE", broken)
    with pytest.raises(KeyError):
        pages.respond(Viewer({}), request("/viewer"))
