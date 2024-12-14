ARG PYTHON_VERSION=3.11.11
FROM python:${PYTHON_VERSION}-bookworm AS base

WORKDIR /starplot

# Install required system libraries (GEOS + GDAL)
RUN apt-get clean && apt-get update -y && apt-get install -y libgeos-dev libgdal-dev

# ---------------------------------------------------------------------
FROM base as dev

WORKDIR /starplot

COPY . .

RUN pip install -r requirements.txt
RUN pip install -r requirements-dev.txt

ENV PYTHONPATH=/starplot/src/

RUN git config --global --add safe.directory /starplot

CMD ["bash", "-c", "python -m pytest . && python hash_checks/hashio.py check"]
