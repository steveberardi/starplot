PYTHON=./venv/bin/python
DE421_URL=https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/a_old_versions/de421.bsp
DOCKER_RUN=docker run --rm -it -v $(shell pwd):/starplot starplot bash -c

export PYTHONPATH=./src/

install: venv

lint: venvdev
	$(DOCKER_RUN) "python -m flake8 --ignore E501,W503 src/ tests/"

format:
	$(DOCKER_RUN) "python -m black src/ tests/ scripts/ example.py $(ARGS)"

test:
	$(DOCKER_RUN) "python -m pytest --cov=src/ --cov-report=term --cov-report=html ."


docker-build-test:
	docker build -t starplot-test --target test .

docker-build:
	docker build -t starplot --target dev .

bash:
	$(DOCKER_RUN) bash

shell:
	$(DOCKER_RUN) python

example-map:
	$(DOCKER_RUN) "python /starplot/src/starplot/plot.py"

example:
	$(DOCKER_RUN) "python example.py"

# PyPi - build & publish
build: venv
	$(PYTHON) -m flit build

publish: venv
	$(PYTHON) -m flit publish

ephemeris: venv
	$(PYTHON) -m jplephem excerpt 2001/1/1 2050/1/1 $(DE421_URL) de421sub.bsp

hip8: venv
	$(PYTHON) ./scripts/hip.py hip_main.dat hip8.dat

clean:
	rm -rf __pycache__
	rm -rf venv
	rm -rf dist
	rm -rf htmlcov

.PHONY: install shell build publish clean example
