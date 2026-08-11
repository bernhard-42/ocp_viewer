# ocp_viewer

The standalone OCP CAD viewer: a browser page and the server behind it.

```bash
python -m ocp_viewer
```

Then `show()` from any Python process — the same `show` you would use with the VS Code extension, pointed at this viewer's port.

## What is here, and what is not

Almost nothing about *viewing* is here. The show pipeline, the config semantics, the render and camera policy, the tree state, the measurement backend, the splash logo, the port registry and the wire protocol are all [`ocp-viewer-core`](../ocp-viewer-core), shared with the VS Code extension, Jupyter CadQuery and build123d Studio. What is left is a Flask app: a page, a websocket, and the settings that reach them.

That is the point of the split rather than a side effect of it. A camera that behaves differently here than in VS Code is a bug in one of them, and there is now one place to fix it.

| file | what |
| --- | --- |
| `__init__.py` | `create_app` — the factory, and `serve` for the command line |
| `__main__.py` | the CLI; every option is a viewer setting |
| `config.py` | defaults, the config file, and the command line on top of both |
| `viewer.py` | what a running viewer knows: its two clients, its config, its state |
| `views.py` | the page, and a redirect to it |
| `sockets.py` | the one websocket, and the six kinds of message on it |
| `comms.py` | this host's transport: the browser, already connected |
| `network.py` | is something already listening on that port |

## Settings

Three sources, later winning over earlier:

1. the defaults in `config.py`
2. `~/.ocpvscode_standalone`, if it exists — write one with `python -m ocp_viewer --create_configfile`
3. the command line — `python -m ocp_viewer --help`

The file keeps its old name so that an existing one still works.

## Development

```bash
make install      # editable
make assets       # copy the renderer and the core into static/
make check        # ruff check + ty check, and no formatter
make run
```

`make assets` copies JavaScript out of `node_modules`: three-cad-viewer and ocp-viewer-core are npm packages, taken as tarballs until they are published. `make reload-assets` rebuilds after either of them changes — the `yarn cache clean` in it is not optional, because yarn caches a file dependency by name and version and will otherwise reinstall a stale tarball.

## Licence

Apache-2.0.
