FROM python:3.9.17-bullseye as base

WORKDIR /starplot

RUN apt-get update -y && apt-get install  -y libgeos-dev libgdal-dev

COPY . .

# install fonts
RUN mkdir -p /usr/share/fonts/truetype
RUN wget https://github.com/google/fonts/raw/main/ofl/gfsdidot/GFSDidot-Regular.ttf -P /tmp/fonts
RUN install -m644 /tmp/fonts/*.ttf /usr/share/fonts/truetype/
RUN fc-cache -f

RUN pip install -r requirements.txt
RUN pip install -r requirements-dev.txt

# Install shapely from source to avoid cartopy segfault
# https://stackoverflow.com/questions/52374356/
RUN pip uninstall -y shapely
RUN pip install --no-binary :all: shapely

ENV PYTHONPATH=/starplot/src/

# TEST - Lint, Format, Tests
FROM base as test
RUN make lint && make format ARGS=--check && make test

FROM base as dev
CMD ["bash"]

