# Changelog

## v1.1.0 (2026-09-09)

The first release. 1.0.0 was the version the package carried while it was built and was never published.

- The server is `websockets`' threaded server; Flask and flask-sock are gone. A config sent behind a large model used to reach the browser first and unreadable: the old server compressed and wrote the browser's socket from several threads with nothing serializing them. `websockets` holds a lock for the whole of a send, compression is off (a model is mostly base64 textures; deflate cost seconds per show for a quarter less on the wire), and the page and its files are answered from the same server.
- Ctrl-C stops the server on Windows too, and with a page connected on every platform.
- A package built without its copied-in assets says so at start, and the README says to run `make assets` before a local install from a checkout.
- Command-line options are choices by where their value came from, not by comparing it to the default, which click 8.5 broke for flags: `--axes0` off and `--timeit` off were being recorded on every start.
- `--timeit` and `--debug` reach a client's `show()` (needs ocp-viewer-core 1.0.6, the floor).
- `make assets` creates the css directory it copies into.
- 78 tests, most of them against the real server run in-process.
