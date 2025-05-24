PYTHON=./venv/bin/python
DE421_URL=https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/a_old_versions/de421.bsp

ifeq ($(CI), true)
 DR_ARGS=
else
 DR_ARGS=-it --env-file ./.env
endif

ifeq ($(PROFILE), true)
 SCRATCH_ARGS=-m cProfile -o results.prof
else
 SCRATCH_ARGS=
endif

DOCKER_RUN=docker run --rm $(DR_ARGS) -v $(shell pwd):/starplot starplot-dev bash -c
DOCKER_BUILDER=starplot-builder

DOCKER_BUILD_PYTHON=docker build -t starplot-$(PYTHON_VERSION) $(DOCKER_BUILD_ARGS) --build-arg="PYTHON_VERSION=$(PYTHON_VERSION)" --target dev .
DOCKER_RUN_PYTHON_TEST=docker run --rm $(DR_ARGS) starplot-$(PYTHON_VERSION)

export PYTHONPATH=./src/

# ------------------------------------------------------------------
build: PYTHON_VERSION=3.11.11
build: DOCKER_BUILD_ARGS=-t starplot-dev
build:
	touch -a .env
	$(DOCKER_BUILD_PYTHON)

docker-multi-arch:
	docker buildx inspect $(DOCKER_BUILDER) && echo "Builder already exists!" || docker buildx create --name $(DOCKER_BUILDER) --bootstrap --use
	docker buildx build --push --platform linux/arm64/v8,linux/amd64 --tag sberardi/starplot-base:latest --target base .

lint:
	$(DOCKER_RUN) "ruff check src/ tests/ hash_checks/ $(ARGS)"

format:
	$(DOCKER_RUN) "python -m black src/ tests/ scripts/ examples/ hash_checks/ tutorial/ data/ $(ARGS)"

test:
	$(DOCKER_RUN) "python -m pytest --cov=src/ --cov-report=term --cov-report=html ."

check-hashes:
	$(DOCKER_RUN) "python hash_checks/hashio.py check"

lock-hashes:
	$(DOCKER_RUN) "python hash_checks/hashio.py lock"

mypy:
	$(DOCKER_RUN) "mypy --ignore-missing-imports src/starplot/"

bash:
	$(DOCKER_RUN) bash

shell:
	$(DOCKER_RUN) ipython

scratchpad:
	$(DOCKER_RUN) "python $(SCRATCH_ARGS) scripts/scratchpad.py"

examples:
	$(DOCKER_RUN) "cd examples && rm -f *.png && rm -f *.jpg && python examples.py"

tutorial:
	$(DOCKER_RUN) "cd tutorial && python build.py"

profile: DR_ARGS=-it -p 8080:8080
profile:
	$(DOCKER_RUN) "python -m cProfile -o temp/results.prof scripts/scratchpad.py && \
	snakeviz -s -p 8080 -H 0.0.0.0 temp/results.prof"

# builds ALL data files and then database:
db: 
	@$(DOCKER_RUN) "python data/scripts/db.py"

build-data-clean:
	mkdir -p data/build
	rm -rf data/build/*

build-stars-mag11:
	@$(DOCKER_RUN) "python data/scripts/bigsky_mag11.py"

build-dsos:
	@$(DOCKER_RUN) "python data/scripts/dsos.py"

build-star-designations:
	@$(DOCKER_RUN) "python data/scripts/star_designations.py"

build-constellations:
	@$(DOCKER_RUN) "python data/scripts/constellations.py"

build-doc-data:
	@$(DOCKER_RUN) "python data/scripts/docdata.py"

version:
	@$(DOCKER_RUN) "python -c 'import starplot as sp; print(sp.__version__)'"

# ------------------------------------------------------------------
# Python version testing
# ------------------------------------------------------------------
test-3.9: PYTHON_VERSION=3.9.21
test-3.9:
	$(DOCKER_BUILD_PYTHON)
	$(DOCKER_RUN_PYTHON_TEST)

test-3.10: PYTHON_VERSION=3.10.16
test-3.10:
	$(DOCKER_BUILD_PYTHON)
	$(DOCKER_RUN_PYTHON_TEST)

test-3.11: PYTHON_VERSION=3.11.11
test-3.11:
	$(DOCKER_BUILD_PYTHON)
	$(DOCKER_RUN_PYTHON_TEST)

test-3.12: PYTHON_VERSION=3.12.8
test-3.12:
	$(DOCKER_BUILD_PYTHON)
	$(DOCKER_RUN_PYTHON_TEST)

# Python 3.13 not supported yet!
test-3.13: PYTHON_VERSION=3.13.1
test-3.13:
	$(DOCKER_BUILD_PYTHON)
	$(DOCKER_RUN_PYTHON_TEST)

# ------------------------------------------------------------------
# Docs
docs-serve: DR_ARGS=-it -p 8000:8000
docs-serve:
	$(DOCKER_RUN) "mkdocs serve -a 0.0.0.0:8000 -q --watch src/"

docs-build:
	$(DOCKER_RUN) "mkdocs build"

docs-publish:
	$(DOCKER_RUN) "mkdocs gh-deploy --force"

# ------------------------------------------------------------------
# PyPi - build & publish
flit-build:
	$(DOCKER_RUN) "python -m flit build"

flit-publish: DR_ARGS=-e FLIT_USERNAME -e FLIT_PASSWORD
flit-publish:
	$(DOCKER_RUN) "python -m flit publish"

flit-install:
	FLIT_ROOT_INSTALL=1 flit install

# ------------------------------------------------------------------
# Utils
ephemeris:
	$(DOCKER_RUN) "python -m jplephem excerpt 2025/1/1 2050/1/1 $(DE421_URL) de421sub.bsp"

hip8:
	$(DOCKER_RUN) "python ./scripts/hip.py ./src/starplot/data/library/hip_main.dat hip8.dat 15"

scripts:
	$(DOCKER_RUN) "python ./scripts/$(SCRIPT).py"

allsky:
	$(DOCKER_RUN) "python ./scripts/temp/allsky.py"

clean:
	rm -rf __pycache__
	rm -rf venv
	rm -rf dist
	rm -rf site
	rm -rf htmlcov
	rm -f tests/data/*.png

.PHONY: build test shell flit-build flit-publish clean ephemeris hip8 scratchpad examples scripts tutorial prep-dsos prep-constellations
