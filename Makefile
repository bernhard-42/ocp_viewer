.PHONY: clean bump install check tests dist assets wheel run create-release

PYCACHE := $(shell find . -name '__pycache__')
EGGS := $(wildcard *.egg-info)
CURRENT_VERSION := $(shell awk '/current_version =/ {print substr($$3, 2, length($$3)-2)}' pyproject.toml)

clean:
	@echo "=> Cleaning"
	@rm -fr build dist $(EGGS) $(PYCACHE)

bump:
	@echo Current version: $(CURRENT_VERSION)
ifdef part
	bump-my-version bump $(part) --allow-dirty && grep current pyproject.toml
else ifdef version
	bump-my-version bump --allow-dirty --new-version $(version) && grep current pyproject.toml
else
	@echo "Provide part=major|minor|patch or version=x.y.z"
	exit 1
endif

install:
	uv pip install -e .

# The whole toolchain, as in ocp-viewer-core: no formatter, on purpose.
check:
	uvx ruff@0.16.0 check ocp_viewer/
	uvx ty@0.0.62 check ocp_viewer/

# The CLI tests spawn a real viewer on a port of their own and ask it real
# questions, so they need no viewer running and disturb none that is.
tests:
	OCP_VIEWER_PYTEST=1 pytest -q tests/

# The page loads three files it does not own: the renderer, the shared viewer
# logic, and the renderer's stylesheet. They come from npm packages and are
# copied in rather than vendored, so a rebuilt tarball is one command away.
# `yarn cache clean` is not optional - yarn caches a file dependency by name and
# version, so a rebuilt tarball whose version has not moved installs stale.
assets:
	yarn install --check-files
	@mkdir -p ocp_viewer/server/static/js/ocp-viewer-core ocp_viewer/server/static/css
	@cp node_modules/three-cad-viewer/dist/three-cad-viewer.esm.js ocp_viewer/server/static/js/
	@cp node_modules/three-cad-viewer/dist/three-cad-viewer.css ocp_viewer/server/static/css/
	@cp node_modules/ocp-viewer-core/src/*.js ocp_viewer/server/static/js/ocp-viewer-core/
	@echo "=> Assets copied into static/"

reload-assets:
	yarn remove ocp-viewer-core three-cad-viewer || true
	yarn cache clean
	yarn add ../ocp-viewer-core/dist/ocp-viewer-core-v$(shell awk '/current_version =/ {print substr($$3, 2, length($$3)-2)}' ../ocp-viewer-core/pyproject.toml).tgz
	yarn add ../three-cad-viewer/$(shell cd ../three-cad-viewer && ls three-cad-viewer-v*.tgz | sort -V | tail -n 1)
	@$(MAKE) assets

dist: clean assets
	@python -m build -n
	@ls -l dist/

run:
	python -m ocp_viewer

# Push, then a GitHub release for the version the tree carries, with the wheel
# and the sdist PyPI got. Both must exist in dist/ - `make dist` builds them -
# or nothing is pushed; `gh` creates the tag when there is none yet.
create-release:
	@for f in dist/ocp_viewer-$(CURRENT_VERSION)-py3-none-any.whl \
	         dist/ocp_viewer-$(CURRENT_VERSION).tar.gz; do \
	    test -f $$f || { echo "missing $$f - run make dist first"; exit 1; }; \
	done
	@git push
	@git push --tags
	@gh release create v$(CURRENT_VERSION) \
	    "dist/ocp_viewer-$(CURRENT_VERSION)-py3-none-any.whl#ocp_viewer $(CURRENT_VERSION) - wheel (PyPI)" \
	    "dist/ocp_viewer-$(CURRENT_VERSION).tar.gz#ocp_viewer $(CURRENT_VERSION) - source (PyPI)" \
	    --title "ocp_viewer $(CURRENT_VERSION)" \
	    --notes "ocp_viewer $(CURRENT_VERSION) on PyPI. See CHANGELOG.md." \
	    --target main
