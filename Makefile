PYTHON=./venv/bin/python
DE421_URL=https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/a_old_versions/de421.bsp

ifeq ($(CI), true)
 DR_ARGS=
else
 DR_ARGS=-it
endif

DOCKER_RUN=docker run --rm $(DR_ARGS) -v $(shell pwd):/starplot starplot bash -c

export PYTHONPATH=./src/

lint:
	$(DOCKER_RUN) "python -m flake8 --ignore E501,W503 src/ tests/"

format:
	$(DOCKER_RUN) "python -m black src/ tests/ scripts/ example.py $(ARGS)"

test:
	$(DOCKER_RUN) "python -m pytest --cov=src/ --cov-report=term --cov-report=html ."

docker-build:
	docker build -t starplot --target dev .

bash:
	$(DOCKER_RUN) bash

shell:
	$(DOCKER_RUN) python

example:
	$(DOCKER_RUN) "python example.py"

docs-serve:
	docker run --rm -it -p 8000:8000 -v $(shell pwd):/starplot starplot bash -c "mkdocs serve -a 0.0.0.0:8000"


# PyPi - build & publish
build:
	$(DOCKER_RUN) "python -m flit build"

# TODO : move publish to docker
publish:
	$(PYTHON) -m flit publish

ephemeris:
	$(DOCKER_RUN) "python -m jplephem excerpt 2001/1/1 2050/1/1 $(DE421_URL) de421sub.bsp"

hip8:
	$(DOCKER_RUN) "python ./scripts/hip.py hip_main.dat hip8.dat"

clean:
	rm -rf __pycache__
	rm -rf venv
	rm -rf dist
	rm -rf htmlcov

.PHONY: install shell build publish clean example
