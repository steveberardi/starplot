FROM python:3.11.4-bookworm as base

WORKDIR /starplot

RUN apt-get update -y && apt-get install -y libgeos-dev libgdal-dev

# Install fonts
# not required, but make the maps look better (especially greek letters)
RUN mkdir -p /usr/share/fonts/truetype
RUN wget https://github.com/google/fonts/raw/main/ofl/gfsdidot/GFSDidot-Regular.ttf -P /tmp/fonts
RUN install -m644 /tmp/fonts/*.ttf /usr/share/fonts/truetype/
RUN fc-cache -f

# ---------------------------------------------------------------------
FROM python:3.10.12-bookworm as base310

WORKDIR /starplot

RUN apt-get update -y && apt-get install -y libgeos-dev libgdal-dev

# MAYBE REQUIRED for Python 3.10.x? TODO: investigate more
# Install shapely from source to avoid cartopy segfault
# https://stackoverflow.com/questions/52374356/
RUN pip install --no-binary :all: shapely==2.0.1

# ---------------------------------------------------------------------
FROM base as dev

WORKDIR /starplot

COPY . .

RUN pip install -r requirements.txt
RUN pip install -r requirements-dev.txt

ENV PYTHONPATH=/starplot/src/

RUN git config --global --add safe.directory /starplot

CMD ["bash"]
