# Changelog

## unreleased

- **Viewer changes**

    - **Features**
        - To measure a plugin's objects, install the plugin in the environment `ocp_viewer` runs in
        - `cursor_pivot` and `zoom_to_cursor` switch rotating around and zooming towards the cursor off separately, with `show`, `set_defaults`, `set_viewer_config` and the options `--no_cursor_pivot` and `--no_zoom_to_cursor` or the workspace config

    - **Changes**
        - `ocp_viewer` depends on `ocp-viewer-core[cli]>=1.2.0,<1.3.0` (was `>=1.1.3,<1.2.0`): ocp-viewer-core 1.2.0 runs on ocp-tessellate 3.7, which brings the kernel plugins, and has the two cursor options

- **Inherited changes**
    - **from ocp-tessellate 3.7.0** (was 3.6.3)
        - Objects of CAD kernels other than OCCT are shown when the kernel's plugin is installed, alone or mixed with build123d, CadQuery and OCCT objects ([CAD kernel plugins](https://bernhard-42.github.io/ocp_viewer_docs/plugins/overview/)). The first plugin is [ocp-viewer-smlibpy](https://github.com/bernhard-42/ocp-viewer-smlibpy) for SMLib. Nothing changes for OCCT objects
        - An object nothing can draw is left out, passed directly or inside a list, tuple or dict, and its type is named once per show, e.g. `show: skipped smlibpy.shapes.Part (no kernel plugin installed?)`. `None` and other builtin values stay silent, like numbers and strings
        - Finding shared shapes no longer slows down with the square of their number
        - Fix: a face that cannot be meshed no longer shifts the ids of the faces and edges after it, so clicking a face or edge reports that one and the Properties tool measures that one
        - Fix: edges and vertices inside a located assembly are measured where they are drawn, not at the origin, and the view fits them where they are
        - Fix: a build123d builder (`BuildPart`, `BuildSketch`, `BuildLine`, `BuildSheet`) shown with `colors` is drawn in that color, not in its default color, and a part, sketch or sheet also takes the given `alphas`
    - **from ocp-viewer-core 1.2.0** (was 1.1.3)
        - The Distance and Properties tools measure objects of other kernels from that kernel's own geometry, through the kernel's plugin of the measurement backend. A distance between shapes of two kernels is one row saying so
        - `cursor_pivot` and `zoom_to_cursor` switch rotating around and zooming towards the cursor off separately; they are arguments of `show`, `show_object`, `show_objects`, `set_defaults` and `set_viewer_config`, and carry over from show to show
        - `set_viewer_config(shape_filter=...)` sets the topology filter, `"none"` (all), `"vertex"`, `"edge"`, `"face"` or `"solid"`, as the dropdown and the keys `a` / `v` / `e` / `f` / `s` do. Every new model resets it to `"none"`
        - A selection copied with the select tool holds the indices for one object and one kind as before, e.g. `6,16,7,17`. For several objects or kinds it holds one labelled line per object and kind, `# <object path> <kind>` followed by its indices, where it used to mix them into one list that selected the wrong shapes
        - `status()` reports the current selection (`selected`) and the last double-click pick (`lastPick`), each with a counter (`selection_seq`, `pick_seq`) that moves with every new one; a new model clears the last pick
        - A `show` with nothing it can draw prints `show: No CAD objects to show` and sends nothing, so the viewer keeps its model
        - Fix: the Properties tool and the Distance tool's center-to-center put the center of a cylinder or cone face on its axis at the face's middle, not at an end of the surface such as the top of a hole; the center of a planar face is its center of mass, not one of its corners
        - Fix: the Properties tool shows the vertex of a hyperbola, not its center
        - Fix: `progress=None` in `show`, `show_object`, `show_objects` and `show_all` shows no progress, as documented; it printed the default progress
        - Fix: `modes=Render.FACES` (one mode, not a list) applies to every object, as documented; it failed with "object of type 'Render' has no len()"
    - **from three-cad-viewer 5.2.1** (was 5.1.3)
        - A rotate drag that starts on the model turns the camera around the point under the cursor, one that starts on the background around the centre of the visible objects; a small black sphere marks the pivot while dragging. The wheel, trackpad pinch and middle-button drag zoom towards the cursor. Both are on by default; Reset and Recenter put the camera target back ([three-cad-viewer#48](https://github.com/bernhard-42/three-cad-viewer/pull/48), by @Xapphire13)
        - On a touchscreen, a one-finger drag rotates around the point under the finger; two fingers zoom and pan
        - The Info box lists the control type and how it rotates and zooms, and logs each change
        - A double-click picks what the hover highlights: it follows the topology filter (All / Vertex / Edge / Face / Solid), and the bounding box wraps the picked face or edge. A vertex gets a marker, and the info panel names the picked element and shows a vertex's coordinates. A second double-click on the same element removes the box. With the filter on All and the cursor on or near an edge, the edge is picked (vertices before edges, edges before faces); hide (`meta`) and isolate (`shift`) still act on the whole object
        - `lastPick` has the new fields `component`, the full path of what was picked, and `point`, the world coordinates of the double-clicked point, and it is sent on every double-click
        - **Breaking:** `lastPick.boundingBox` and `lastPick.boundingSphere` describe the picked face, edge or vertex, no longer its object; a vertex has a box of size zero. With the filter on Solid, for hide and isolate, for objects that are faces, edges or vertices themselves, and for clicks in the tree they are the object's box as before
        - With `cursor_pivot` on, `shift` + `meta` + double-click on the model no longer sets the camera target, since every rotation already turns around the point under the cursor; with `cursor_pivot` off it does, as before
        - Image faces and the back sides of faces and open shells can be clicked, highlighted and copied like any face ([vscode-ocp-cad-viewer#248](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues/248))
        - The status line shows the clicked point with the platform's copy key (`Cmd+C` on macOS, `Ctrl+C` elsewhere)
        - Selected vertices are drawn larger (8 px instead of 4), also while hovered
        - The help names the platform's modifier keys (`Cmd` / `Option` on macOS, `Win` on Windows, `Super` on Linux) and shows keys in code style
        - Geometry types in the status line and the Properties panel read `B-spline surface` instead of `bspline` or `BSplineSurface`, and `Surface of revolution` instead of `surface of revolution`
        - three.js r187 (was r184), postprocessing 6.39.6
        - Trackball: holding `a`, `s` or `d` no longer changes a drag to rotate, zoom or pan; these keys also reacted to typing elsewhere on the page, and `a` and `s` changed the shape filter at the same time
        - Fix: the topology filter keys `a` / `v` / `e` / `f` / `s` and the select tool's Escape and Backspace act only when the viewer has focus: Cmd-V, or a `v` typed elsewhere such as in a notebook cell, no longer sets the filter to Vertex, and Backspace in a text field no longer removes a selected element
        - Fix: the measurement panel stays fully inside the viewer when it reopens at its previous position after a new model, a smaller viewer or a larger result
        - Fix: turning the select tool off or pressing Escape reports the empty selection
        - Fix: toolbar tooltips and the grid menu are no longer cut off at the toolbar's bottom edge in Safari and other WebKit browsers ([three-cad-viewer#47](https://github.com/bernhard-42/three-cad-viewer/pull/47), by @Xapphire13)
        - Fix: object names containing `<`, `"` or `\` are shown literally, and their tree rows keep working
        - Fix: the view no longer jumps at the first rotation after a `quaternion` that is not exactly unit length, nor again after every Reset
        - Fix: switching the Studio background from a solid color back to Environment draws the environment again
        - Fix: the help names the filter key for all object types correctly, `a`, and shows scrollbars only when it does not fit
        - Fix: a two-finger pinch no longer rotates the view with the holroyd trackball
        - Fix: a long press on the viewer no longer selects it in Safari on iPad and iPhone
        - Fix: Escape with the filter dropdown open closes only the dropdown; the next Escape clears the selection or stops the animation. It used to clear the selection as well, and without a tool it did not close the dropdown

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
