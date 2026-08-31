DE421_URL=https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/a_old_versions/de421.bsp

ifeq ($(CI), true)
 DR_ARGS=-e FLIT_USERNAME -e FLIT_PASSWORD
else
 DR_ARGS=-it 
 #--env-file ./.env
endif

DOTENV=--env-file $(shell pwd)/.env
DOCKER_RUN=docker run --rm $(DR_ARGS) -v $(shell pwd):/starplot starplot-dev bash -c
DOCKER_BUILDER=starplot-builder

DOCKER_BUILD_PYTHON=docker build -t starplot-$(PYTHON_VERSION) $(DOCKER_BUILD_ARGS) --build-arg="PYTHON_VERSION=$(PYTHON_VERSION)" .
DOCKER_RUN_PYTHON_TEST=docker run --rm $(DR_ARGS) starplot-$(PYTHON_VERSION)

# docker run --rm -it -v .:/starplot starplot-3.12.12 bash -c -v $(shell pwd):/starplot

export PYTHONPATH=./src/

# ------------------------------------------------------------------
install:
	uv sync --all-groups --all-extras

build: PYTHON_VERSION=3.12.12
build: DOCKER_BUILD_ARGS=-t starplot-dev
build:
	touch -a .env
	$(DOCKER_BUILD_PYTHON)

env:
	test -f .env || echo "STARPLOT_DATA_PATH=$(CURDIR)/data/" > .env

lint:
	uv run $(DOTENV) ruff check $(ARGS) src/ tests/ hash_checks/ 

format:
	uv run $(DOTENV) ruff format $(ARGS) src/ tests/ scripts/ examples/ hash_checks/ tutorial/ data/

test:
	uv run $(DOTENV) pytest $(ARGS) --cov=src/ --cov-report=term --cov-report=html tests/

check-hashes:
	rm -f hash_checks/data/*.png
	uv run $(DOTENV) python hash_checks/hashio.py check

lock-hashes:
	uv run $(DOTENV) python hash_checks/hashio.py lock

shell:
	uv run $(DOTENV) ipython

marimo: DR_ARGS=-it -p 9009:9009
marimo:
	uv run $(DOTENV) marimo edit scripts/marimo.py --no-token  --host 0.0.0.0 --port 9009

examples:
	cd examples && rm -f *.png && rm -f *.jpg && uv run $(DOTENV) examples.py

tutorial:
	cd tutorial && uv run $(DOTENV) build.py

profile: DR_ARGS=-it -p 8081:8081
profile:
	$(DOCKER_RUN) "python -m cProfile -o temp/results.prof scripts/scratchpad.py && \
	snakeviz -s -p 8081 -H 0.0.0.0 temp/results.prof"

db: 
	uv run $(DOTENV) data/scripts/db.py

build-data-clean:
	mkdir -p data/build
	rm -rf data/build/*

build-star-designations:
	uv run $(DOTENV) data/scripts/star_designations.py

version:
	uv run $(DOTENV) python -c 'import starplot as sp; print(sp.__version__)'

setup:
	uv run $(DOTENV) starplot setup

download-test-fonts:
	uv run $(DOTENV) scripts/download_test_fonts.py

# ------------------------------------------------------------------
# Python version testing
# ------------------------------------------------------------------
test-3.10: PYTHON_VERSION=3.10.21
test-3.10:
	$(DOCKER_BUILD_PYTHON)
	$(DOCKER_RUN_PYTHON_TEST)

test-3.11: PYTHON_VERSION=3.11.16
test-3.11:
	$(DOCKER_BUILD_PYTHON)
	$(DOCKER_RUN_PYTHON_TEST)

test-3.12: PYTHON_VERSION=3.12.14
test-3.12:
	$(DOCKER_BUILD_PYTHON)
	$(DOCKER_RUN_PYTHON_TEST)

test-3.13: PYTHON_VERSION=3.13.15
test-3.13:
	$(DOCKER_BUILD_PYTHON)
	$(DOCKER_RUN_PYTHON_TEST)

# there are warnings with 3.14, but tests/checks pass
# needs more investigation
test-3.14: PYTHON_VERSION=3.14.7
test-3.14:
	$(DOCKER_BUILD_PYTHON)
	$(DOCKER_RUN_PYTHON_TEST)

# ------------------------------------------------------------------
# Docs
docs-serve:
	uv run $(DOTENV) zensical serve

docs-build:
	uv run $(DOTENV) zensical build -c

docs-references:
	uv run $(DOTENV) docs/scripts/data.py
	uv run $(DOTENV) docs/scripts/markers.py
	uv run $(DOTENV) docs/scripts/gradients.py
	uv run $(DOTENV) docs/scripts/projections.py
	uv run $(DOTENV) docs/scripts/projection_list.py
	uv run $(DOTENV) docs/scripts/style_explorer.py

docs: docs-references docs-build


# ------------------------------------------------------------------
# PyPi - build & publish
flit-build:
	uv run $(DOTENV) flit build

flit-publish:
	uv run $(DOTENV) flit publish

flit-install:
	FLIT_ROOT_INSTALL=1 flit install

# ------------------------------------------------------------------
# Utils
ephemeris:
	$(DOCKER_RUN) "python -m jplephem excerpt 2025/1/1 2050/1/1 $(DE421_URL) de421sub.bsp"

scripts:
	uv run $(DOTENV) python ./scripts/$(SCRIPT).py

list-fonts:
	uv run $(DOTENV) python ./scripts/list_fonts.py

clean:
	rm -rf __pycache__
	rm -rf venv
	rm -rf dist
	rm -rf site
	rm -rf htmlcov
	rm -f tests/data/*.png

.PHONY: build test shell flit-build flit-publish clean ephemeris examples scripts tutorial list-fonts
