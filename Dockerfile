ARG PYTHON_VERSION=3.12.12
FROM python:${PYTHON_VERSION}-bookworm

WORKDIR /starplot

COPY . .

# Install Chinese font
# Noto Sans SC -> https://fonts.google.com/noto/specimen/Noto+Sans+SC
RUN mkdir -p /usr/share/fonts/truetype
RUN wget https://github.com/google/fonts/raw/refs/heads/main/ofl/notosanssc/NotoSansSC%5Bwght%5D.ttf -P /tmp/fonts
RUN install -m644 /tmp/fonts/*.ttf /usr/share/fonts/truetype/
RUN fc-cache -f

RUN pip install uv
RUN uv pip install --system -r requirements.txt
RUN uv pip install --system -r requirements-dev.txt

ENV PYTHONPATH=/starplot/src/

RUN git config --global --add safe.directory /starplot

# Build database
RUN python data/scripts/db.py

CMD ["bash", "-c", "python -m pytest . && python hash_checks/hashio.py check"]
