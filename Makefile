PYTHON=./venv/bin/python
DE421_URL=https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/a_old_versions/de421.bsp

ifeq ($(CI), true)
 DR_ARGS=-e FLIT_USERNAME -e FLIT_PASSWORD
else
 DR_ARGS=-it --env-file ./.env
endif

DOCKER_RUN=docker run --rm $(DR_ARGS) -v $(shell pwd):/starplot starplot-dev bash -c
DOCKER_BUILDER=starplot-builder

DOCKER_BUILD_PYTHON=docker build -t starplot-$(PYTHON_VERSION) $(DOCKER_BUILD_ARGS) --build-arg="PYTHON_VERSION=$(PYTHON_VERSION)" .
DOCKER_RUN_PYTHON_TEST=docker run --rm $(DR_ARGS) starplot-$(PYTHON_VERSION)

export PYTHONPATH=./src/

# ------------------------------------------------------------------
build: PYTHON_VERSION=3.12.12
build: DOCKER_BUILD_ARGS=-t starplot-dev
build:
	touch -a .env
	$(DOCKER_BUILD_PYTHON)

lint:
	uv run ruff check src/ tests/ hash_checks/ $(ARGS)

format:
	uv run ruff format src/ tests/ scripts/ examples/ hash_checks/ tutorial/ data/ $(ARGS)

test:
	uv run pytest $(ARGS) --cov=src/ --cov-report=term --cov-report=html tests/

check-hashes:
	uv run python hash_checks/hashio.py check

lock-hashes:
	uv run python hash_checks/hashio.py lock

shell:
	uv run ipython

marimo: DR_ARGS=-it -p 9009:9009
marimo:
	uv run marimo edit scripts/marimo.py --no-token  --host 0.0.0.0 --port 9009

examples:
	cd examples && rm -f *.png && rm -f *.jpg && uv run examples.py

tutorial:
	cd tutorial && uv run build.py

profile: DR_ARGS=-it -p 8081:8081
profile:
	$(DOCKER_RUN) "python -m cProfile -o temp/results.prof scripts/scratchpad.py && \
	snakeviz -s -p 8081 -H 0.0.0.0 temp/results.prof"

# builds ALL data files and then database:
db: 
	uv run data/scripts/db.py

build-data-clean:
	mkdir -p data/build
	rm -rf data/build/*

build-star-designations:
	uv run data/scripts/star_designations.py

build-doc-data:
	uv run data/scripts/docdata.py

version:
	uv run python -c 'import starplot as sp; print(sp.__version__)'

install:
	uv sync --all-groups --all-extras

# ------------------------------------------------------------------
# Python version testing
# ------------------------------------------------------------------
test-3.10: PYTHON_VERSION=3.10.19
test-3.10:
	$(DOCKER_BUILD_PYTHON)
	$(DOCKER_RUN_PYTHON_TEST)

test-3.11: PYTHON_VERSION=3.11.14
test-3.11:
	$(DOCKER_BUILD_PYTHON)
	$(DOCKER_RUN_PYTHON_TEST)

test-3.12: PYTHON_VERSION=3.12.12
test-3.12:
	$(DOCKER_BUILD_PYTHON)
	$(DOCKER_RUN_PYTHON_TEST)

test-3.13: PYTHON_VERSION=3.13.8
test-3.13:
	$(DOCKER_BUILD_PYTHON)
	$(DOCKER_RUN_PYTHON_TEST)

# ------------------------------------------------------------------
# Docs
docs-serve:
	uv run zensical serve

docs-build:
	uv run zensical build

# ------------------------------------------------------------------
# PyPi - build & publish
flit-build:
	$(DOCKER_RUN) "python -m flit build"

flit-publish:
	$(DOCKER_RUN) "python -m flit publish"

flit-install:
	FLIT_ROOT_INSTALL=1 flit install

# ------------------------------------------------------------------
# Utils
ephemeris:
	$(DOCKER_RUN) "python -m jplephem excerpt 2025/1/1 2050/1/1 $(DE421_URL) de421sub.bsp"

scripts:
	$(DOCKER_RUN) "python ./scripts/$(SCRIPT).py"

clean:
	rm -rf __pycache__
	rm -rf venv
	rm -rf dist
	rm -rf site
	rm -rf htmlcov
	rm -f tests/data/*.png

.PHONY: build test shell flit-build flit-publish clean ephemeris examples scripts tutorial
