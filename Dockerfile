ARG PYTHON_VERSION=3.11.11
FROM python:${PYTHON_VERSION}-bookworm AS base

WORKDIR /starplot

# Install required system libraries (GEOS + GDAL)
RUN apt-get clean && apt-get update -y && apt-get install -y libgeos-dev libgdal-dev

# ---------------------------------------------------------------------
FROM base AS dev

WORKDIR /starplot

COPY . .

RUN pip install -r requirements.txt
RUN pip install -r requirements-dev.txt

ENV PYTHONPATH=/starplot/src/

RUN git config --global --add safe.directory /starplot

RUN mkdir -p data/build
RUN python data/scripts/bigsky_mag11.py
RUN python data/scripts/dsos.py
RUN python data/scripts/star_designations.py
RUN python data/scripts/constellations.py
RUN python data/scripts/db.py
RUN python data/scripts/docdata.py

CMD ["bash", "-c", "python -m pytest . && python hash_checks/hashio.py check"]
