ARG PYTHON_VERSION=3.11.7
FROM python:${PYTHON_VERSION}-bookworm AS base

WORKDIR /starplot

RUN apt-get update -y && apt-get install -y libgeos-dev libgdal-dev

# Install fonts
# not required, but make the maps look better (especially greek letters)
RUN mkdir -p /usr/share/fonts/truetype
RUN wget https://github.com/google/fonts/raw/main/ofl/gfsdidot/GFSDidot-Regular.ttf -P /tmp/fonts
RUN install -m644 /tmp/fonts/*.ttf /usr/share/fonts/truetype/
RUN fc-cache -f

# ---------------------------------------------------------------------
FROM base as dev

WORKDIR /starplot

COPY . .

RUN pip install -r requirements.txt
RUN pip install -r requirements-dev.txt

ENV PYTHONPATH=/starplot/src/

RUN git config --global --add safe.directory /starplot

CMD ["bash", "-c", "python -m pytest ."]
