ARG PYTHON_VERSION=3.11.11
FROM python:${PYTHON_VERSION}-bookworm AS base

WORKDIR /starplot

# ---------------------------------------------------------------------
FROM base AS dev

WORKDIR /starplot

COPY . .

RUN pip install uv
RUN uv pip install --system -r requirements.txt
RUN uv pip install --system -r requirements-dev.txt

ENV PYTHONPATH=/starplot/src/

RUN git config --global --add safe.directory /starplot

# Build database
RUN python data/scripts/db.py

CMD ["bash", "-c", "python -m pytest . && python hash_checks/hashio.py check"]
