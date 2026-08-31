ARG PYTHON_VERSION=3.12.14
FROM python:${PYTHON_VERSION}-trixie

WORKDIR /starplot

COPY . .

ENV UV_PROJECT_ENVIRONMENT=/usr/local
ENV STARPLOT_DATA_PATH=/starplot/data
ENV PYTHONPATH=/starplot/src/

# Install Cairo (for PNG exports)
RUN apt update && apt install libcairo2-dev

RUN pip install uv
RUN uv sync --all-groups --all-extras

RUN git config --global --add safe.directory /starplot

# Build database
RUN uv run data/scripts/db.py

# Install fonts etc
RUN uv run starplot setup

# Install fonts used in tests
RUN uv run scripts/download_test_fonts.py

CMD ["bash", "-c", "uv run pytest . && uv run hash_checks/hashio.py check"]
