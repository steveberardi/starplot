PYTHON=./venv/bin/python
DE421_URL=https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/a_old_versions/de421.bsp

ifeq ($(CI), true)
 DR_ARGS=
else
 DR_ARGS=-it
endif

ifeq ($(PROFILE), true)
 SCRATCH_ARGS=-m cProfile -o results.prof
else
 SCRATCH_ARGS=
endif

DOCKER_RUN=docker run --rm $(DR_ARGS) -v $(shell pwd):/starplot starplot-dev bash -c
DOCKER_BUILDER=starplot-builder

DOCKER_BUILD_PYTHON=docker build -t starplot-$(PYTHON_VERSION) $(DOCKER_BUILD_ARGS) --build-arg="PYTHON_VERSION=$(PYTHON_VERSION)" --target dev .
DOCKER_RUN_PYTHON_TEST=docker run --rm $(DR_ARGS) -v $(shell pwd):/starplot starplot-$(PYTHON_VERSION)

export PYTHONPATH=./src/

# ------------------------------------------------------------------
build: PYTHON_VERSION=3.11.7
build: DOCKER_BUILD_ARGS=-t starplot-dev
build:
	$(DOCKER_BUILD_PYTHON)

docker-multi-arch:
	docker buildx inspect $(DOCKER_BUILDER) && echo "Builder already exists!" || docker buildx create --name $(DOCKER_BUILDER) --bootstrap --use
	docker buildx build --push --platform linux/arm64/v8,linux/amd64 --tag sberardi/starplot-base:latest --target base .

lint:
	$(DOCKER_RUN) "ruff check src/ tests/"

format:
	$(DOCKER_RUN) "python -m black src/ tests/ scripts/ examples/ $(ARGS)"

test:
	$(DOCKER_RUN) "python -m pytest --cov=src/ --cov-report=term --cov-report=html ."

bash:
	$(DOCKER_RUN) bash

shell:
	$(DOCKER_RUN) python

scratchpad:
	$(DOCKER_RUN) "python $(SCRATCH_ARGS) scripts/scratchpad.py"

examples:
	$(DOCKER_RUN) "cd examples && python examples.py"

# ------------------------------------------------------------------
# Python version testing
# ------------------------------------------------------------------
test-3.9: PYTHON_VERSION=3.9.18
test-3.9:
	$(DOCKER_BUILD_PYTHON)
	$(DOCKER_RUN_PYTHON_TEST)

test-3.10: PYTHON_VERSION=3.10.13
test-3.10:
	$(DOCKER_BUILD_PYTHON)
	$(DOCKER_RUN_PYTHON_TEST)

test-3.11: PYTHON_VERSION=3.11.7
test-3.11:
	$(DOCKER_BUILD_PYTHON)
	$(DOCKER_RUN_PYTHON_TEST)

test-3.12: PYTHON_VERSION=3.12.1
test-3.12:
	$(DOCKER_BUILD_PYTHON)
	$(DOCKER_RUN_PYTHON_TEST)

# ------------------------------------------------------------------
# Docs
docs-serve: DR_ARGS=-it -p 8000:8000
docs-serve:
	$(DOCKER_RUN) "mkdocs serve -a 0.0.0.0:8000 --watch src/"

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

# ------------------------------------------------------------------
# Utils
ephemeris:
	$(DOCKER_RUN) "python -m jplephem excerpt 2001/1/1 2050/1/1 $(DE421_URL) de421sub.bsp"

hip8:
	$(DOCKER_RUN) "python ./scripts/hip.py ./src/starplot/data/library/hip_main.dat hip8.dat 15"

scripts:
	$(DOCKER_RUN) "python ./scripts/$(SCRIPT).py"

clean:
	rm -rf __pycache__
	rm -rf venv
	rm -rf dist
	rm -rf site
	rm -rf htmlcov

.PHONY: install test shell flit-build flit-publish clean ephemeris hip8 scratchpad examples scripts
