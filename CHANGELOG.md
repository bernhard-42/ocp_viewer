# Changelog

## v1.1.2 (2026-09-10)

- The viewer page ships ocp-viewer-core JavaScript 1.0.4: a `set_viewer_config(glass=...)` at runtime re-derives the page's geometry instead of leaving it as it was. Leaving glass mode moves the tree out of the canvas's row and three-cad-viewer re-lays out with the `cadWidth` it was given, so the viewer used to grow by the tree's width and overflow the window until the next resize put it right.
- And three-cad-viewer 5.0.6: a resize sizes the toolbar and the tree, not only the canvas. `resizeCadView` passed neither `glass` nor `tools` on to the display, so outside glass mode the toolbar and the body kept the canvas's width while the tree sat beside it, and the tree kept its old height while the canvas grew.
- The core floor is `ocp-viewer-core[cli]>=1.0.8`. `questionary` is an extra there now rather than every host's dependency: its one use is the prompt that asks which viewer to talk to when several are listening, which needs a plain shell - and this is one of the two viewers that has one.

## v1.1.1 (2026-09-09)

- `ImageFace` and the native-tessellator toggles come from `ocp_viewer_core.tessellator`, so nothing here reaches into ocp_tessellate any more. The toggles - `enable_native_tessellator`, `disable_native_tessellator`, `is_native_tessellator_enabled` - are new in this viewer; the other three had them and this one did not. Needs the ocp-viewer-core release that carries `tessellator`, and the floor moves to it when that is published.
- The YAML dependency is declared as `PyYAML`, which is what `settings.py` imports. `pyaml` is a different package that happened to pull it in.

## v1.1.0 (2026-09-09)

The first release. 1.0.0 was the version the package carried while it was built and was never published.

- The server is `websockets`' threaded server; Flask and flask-sock are gone. A config sent behind a large model used to reach the browser first and unreadable: the old server compressed and wrote the browser's socket from several threads with nothing serializing them. `websockets` holds a lock for the whole of a send, compression is off (a model is mostly base64 textures; deflate cost seconds per show for a quarter less on the wire), and the page and its files are answered from the same server.
- Ctrl-C stops the server on Windows too, and with a page connected on every platform.
- A package built without its copied-in assets says so at start, and the README says to run `make assets` before a local install from a checkout.
- Command-line options are choices by where their value came from, not by comparing it to the default, which click 8.5 broke for flags: `--axes0` off and `--timeit` off were being recorded on every start.
- `--timeit` and `--debug` reach a client's `show()` (needs ocp-viewer-core 1.0.6, the floor).
- `make assets` creates the css directory it copies into.
- 78 tests, most of them against the real server run in-process.
