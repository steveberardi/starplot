PYTHON=./venv/bin/python
DE421_URL=https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/a_old_versions/de421.bsp

export PYTHONPATH=./src/

install: venv

lint: venv
	@$(PYTHON) -m flake8 --ignore E501,W503 src/
# @$(PYTHON) -m mypy src/

format: venvdev
	@$(PYTHON) -m black src/ scripts/ example.py $(ARGS)

test: venv
	$(PYTHON) -m pytest --cov=src/ --cov-report=term --cov-report=html .

venvdev: venv requirements-dev.txt
	./venv/bin/pip install -r requirements-dev.txt

venv: requirements.txt
	python -m venv venv
	./venv/bin/pip install -r requirements.txt
	touch venv

shell: venv
	@$(PYTHON)

build: venv
	$(PYTHON) -m flit build

publish: venv
	$(PYTHON) -m flit publish

example: venv
	$(PYTHON) example.py

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
