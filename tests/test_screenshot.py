"""`save_png_data_url`: the file exists only once it is complete."""

import base64

from ocp_viewer.server.screenshot import save_png_data_url

PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 16


def test_writes_the_decoded_image_and_leaves_no_temporary_behind(tmp_path, capsys):
    target = tmp_path / "shot.png"
    data_url = "data:image/png;base64," + base64.b64encode(PNG).decode("ascii")
    save_png_data_url(data_url, str(target))
    assert target.read_bytes() == PNG
    assert [p.name for p in tmp_path.iterdir()] == ["shot.png"]
    assert f"Wrote png file to {target}" in capsys.readouterr().out


def test_an_unwritable_path_is_reported_not_raised(tmp_path, capsys):
    data_url = "data:image/png;base64," + base64.b64encode(PNG).decode("ascii")
    save_png_data_url(data_url, str(tmp_path / "no" / "such" / "dir.png"))
    assert "Cannot save png file" in capsys.readouterr().out
