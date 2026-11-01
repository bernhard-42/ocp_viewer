# Changelog

## Unreleased

- **Features**
    - Rotating and zooming follow the cursor, with trackball and orbit control: a drag that starts on the model rotates around the point under the cursor, and the wheel and trackpad pinch zoom towards the cursor (three-cad-viewer 5.2). New setting `cursor_pivot` (default `true`) in `~/.ocpvscode_standalone` and flags `--cursor_pivot` / `--no_cursor_pivot`; `false` (or `--no_cursor_pivot`) restores rotating and zooming around the target. A config file written by an earlier release has no such key and gets the default

## v1.2.0 (2026-10-13)

- **Features**
    - New setting `python_enumeration` (default `true`) in `~/.ocpvscode_standalone`, flags `--python_enumeration` / `--no_python_enumeration` and keyword `python_enumeration` of `show`, `show_object`, `show_objects` and `set_defaults` ([#242](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/242)): repeated object names are numbered from 0 like Python indices - `Solid(0)`, `Solid(1)`, `Solid(2)` instead of `Solid`, `Solid(2)`, `Solid(3)`. `false` (or `--no_python_enumeration`) restores the former names. A config file written by an earlier release has no such key and gets the default
    - Measured angles show their supplement as well, `60.000 (120.000)`: the distance tool's angle, and the properties tool's angle to XY of a face and of an edge's ends ([#236](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/236)). A cone's half angle stays one number
    - `ColorMap.golden_ratio(..., hue_offset=0.0)` shifts where the golden-ratio color sequence starts, as a fraction of the colormap from 0 to 1; 0 gives the colors as before ([#222](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/222))
    - `save_screenshot(..., timeout_s=2)` sets how long to wait for the file, in seconds
    - nanocct support (ocp-tessellate 3.6): `show()` handles shapes of build123d or CadQuery running on nanocct, and OCP and nanocct objects can be shown together. Where nanocct is installed it is the binding for everything that does not bring its own OCCT object, as in the other libraries of the ecosystem
    - **three-cad-viewer 5.1.3** (was 5.0.6)
        - Hovering a row of the tree highlights that object, or everything below a group: the faces of solids and faces, the edges of objects that have only edges, the vertices of objects that have only vertices ([#218](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/218))
        - Ctrl/Cmd-C over the model copies the point under the mouse to the clipboard as `x, y, z` (4 decimals), and the status line shows `copied: x, y, z`. It follows the topology filter (All / Vertex / Edge / Face / Solid) and needs no click into the viewer first; it is off in explode mode, with a z-scale other than 1, and while an animation has moved the parts (Play or the time slider; Stop turns it back on, Pause does not) ([#243](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/243))
        - Clip caps are hatched: neighbouring solids alternate the direction and spacing of the lines, which stay fixed to the clip plane while the view moves
        - Clip caps are outlined in the edge color while the Clip tab is active, also where caps of touching solids meet and, seen from behind, along the cut contour on the faces. The outline is drawn once the camera has been still for 150 ms

- **Changes**
    - `ocp_viewer` depends on `ocp-viewer-core[cli]>=1.1.0,<1.2.0` (was `>=1.0.10,<1.1.0`): ocp-viewer-core 1.1 runs on ocp-tessellate 3.6
    - The native-tessellator toggles are gone: `enable_native_tessellator()`, `disable_native_tessellator()`, `is_native_tessellator_enabled()` and `init_native_tessellator()` are no longer exported, `NATIVE_TESSELLATOR` in the environment no longer means anything, and importing `ocp_viewer` no longer prints "Found and enabled native tessellator.". ocp-tessellate dropped its native tessellator and `ocp_addons`, and ocp-viewer-core the toggles with it
    - Breaking: repeated object names are numbered from 0 by default (`python_enumeration`, above), so a tree path such as `/Group/Solid(2)` now names the third `Solid`, not the second. Animation tracks, saved states and selections that address such paths need the new names, or `python_enumeration=False` - as the setting, through `set_defaults` or as a show keyword - which restores the former names
    - Breaking, for scripts that import from the libraries directly: `ocp_tessellate` no longer re-exports OCCT classes (`ocp_tessellate.ocp_utils.TopoDS_Shape`, `ocp_tessellate.tessellator.gp_Pnt`, ...), import them from OCP or nanocct; `ocp_viewer_core.measure.get_center` returns `(x, y, z)` instead of a vertex

- **Fixes**
    - The center distance between two build123d parts works; wires, shells, compsolids and compounds failed. The properties tool reports the length of a wire and the area of a shell
    - Reference points (centers of mass) of vertices, edges and compounds of faces, edges or vertices are right; they came out at the origin
    - An unknown matplotlib colormap name (`"mpl:nonexistent"`) is reported as unknown instead of as "not a linear segmented colormap"
    - An object whose `is_empty` is true is shown as the empty placeholder, like an empty list
    - A loaded animation no longer keeps the viewer redrawing the scene on every display frame until it is cleared - also while paused, stopped or never started - which cost constant CPU and GPU time in an idle viewer (three-cad-viewer 5.1.3, [three-cad-viewer #44](https://github.com/bernhard-42/three-cad-viewer/issues/44)). Resuming after a pause no longer jumps ahead by the time spent paused
    - In Safari and other WebKit-based browsers, graphics memory no longer grows to about 25 times the model's size, which let a few large shows crash the page (three-cad-viewer 5.0.7)
    - Clearing or replacing a model no longer leaks the orientation marker's graphics resources (three-cad-viewer 5.0.7)
    - The status line at the bottom of the viewer (hover readout, copied point) is no longer cut off. The page took the window's full height for the viewer and left the browser's 8px body margin out of it, so the canvas ended 8px below the window edge (ocp-viewer-core JavaScript 1.1.0)

## v1.1.3 (2026-09-14)

- `modifier_keys` is one map per platform, `{"macOS": {...}, "default": {...}}`, and the viewer gets the one for the machine it runs on. `meta` rotates, hides and isolates, and `metaKey` is Cmd on macOS but the Windows/Super key on Windows and Linux, which the desktop takes for itself - those chords never reached the page there. The default for Windows and Linux is therefore `meta: altKey, alt: metaKey`; the same shape the VS Code extension, Jupyter CadQuery and build123d Studio store. A `~/.ocpvscode_standalone` from an earlier release holds a single flat map: it is read as this platform's choice, with the shipped default for the other.
- The core floor is `ocp-viewer-core[cli]>=1.0.10`, where `Animation.add_track` refuses an unknown action or ill-shaped values before they are sent.

## v1.1.2 (2026-09-11)

- The core floor is `ocp-viewer-core[cli]>=1.0.9`: there `reset_defaults(port=...)` resets the viewer it names. In 1.0.8 the reset opened a fresh scope over the one the `port` had set, so with two viewers listening the which-port prompt appeared in the middle of a `reset_defaults`, and with one it reset whichever discovery found.
- The viewer page ships ocp-viewer-core JavaScript 1.0.4: a `set_viewer_config(glass=...)` at runtime re-derives the page's geometry instead of leaving it as it was. Leaving glass mode moves the tree out of the canvas's row and three-cad-viewer re-lays out with the `cadWidth` it was given, so the viewer used to grow by the tree's width and overflow the window until the next resize put it right.
- And three-cad-viewer 5.0.6: a resize sizes the toolbar and the tree, not only the canvas. `resizeCadView` passed neither `glass` nor `tools` on to the display, so outside glass mode the toolbar and the body kept the canvas's width while the tree sat beside it, and the tree kept its old height while the canvas grew.
- `questionary` is an extra of the core now rather than every host's dependency: its one use is the prompt that asks which viewer to talk to when several are listening, which needs a plain shell - and this is one of the two viewers that has one.

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
