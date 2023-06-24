# FROM ubuntu:22.04 as base
FROM python:3.9.17 as base

# RUN apt-get update && apt-get install -y python3.9 python3-pip python-is-python3
# RUN sudo apt install python-is-python3
WORKDIR /starplot

COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy source code
COPY ./src /starplot/src

# Lint, Format, Tests
FROM base as test
COPY ./tests /starplot/tests
COPY requirements-dev.txt .
RUN pip install -r requirements-dev.txt
COPY Makefile /starplot

ENV PYTHONPATH=./src/
RUN python -m pytest --cov=src/ --cov-report=term --cov-report=html .


