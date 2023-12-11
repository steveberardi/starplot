apt update -y && apt-get install -y libgeos-dev libgdal-dev

# MAYBE REQUIRED for Python 3.10.x? TODO: investigate more
# Install shapely from source to avoid cartopy segfault
# https://stackoverflow.com/questions/52374356/
# pip install --no-binary :all: shapely==2.0.1

# Install better font for greek letters
mkdir -p /usr/share/fonts/truetype
wget https://github.com/google/fonts/raw/main/ofl/gfsdidot/GFSDidot-Regular.ttf -P /tmp/fonts
install -m644 /tmp/fonts/*.ttf /usr/share/fonts/truetype/
fc-cache -f

pip install -r requirements.txt
pip install -r requirements-dev.txt
