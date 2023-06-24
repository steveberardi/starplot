FROM python:3.9.17-bullseye as base

WORKDIR /starplot

COPY requirements.txt pyproject.toml .

# Copy source code
COPY ./src /starplot/src
COPY ./scripts /starplot/scripts
COPY example.py .

# Lint, Format, Tests
FROM base as test
COPY ./tests /starplot/tests
COPY requirements-dev.txt Makefile .
# RUN pip install -r requirements-dev.txt

RUN make format ARGS=--check && make lint && make test
# RUN python -m pytest --cov=src/ --cov-report=term --cov-report=html .


