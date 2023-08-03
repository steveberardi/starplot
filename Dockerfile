FROM sberardi/starplot-base as base

WORKDIR /starplot

# Install fonts
# not required, but makes the maps look better (especially greek letters)
RUN mkdir -p /usr/share/fonts/truetype
RUN wget https://github.com/google/fonts/raw/main/ofl/gfsdidot/GFSDidot-Regular.ttf -P /tmp/fonts
RUN install -m644 /tmp/fonts/*.ttf /usr/share/fonts/truetype/
RUN fc-cache -f

COPY . .

RUN pip install -r requirements.txt
RUN pip install -r requirements-dev.txt

ENV PYTHONPATH=/starplot/src/

RUN git config --global --add safe.directory /starplot

CMD ["bash"]
