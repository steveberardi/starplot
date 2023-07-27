Starplot is available on [PyPI](https://pypi.org/project/starplot/), but it's basically just a thin layer on top of Matplotlib, Skyfield, Cartopy, and others. So, before installing Starplot you'll need a few dependencies. Below are instructions for installing on macOS and Linux.

## Required Dependencies

- GEOS
- GDAL
- Shapely

## macOS

1. Install required system libraries (via [Homebrew](https://brew.sh/)): 
```
brew install geos gdal
```

2. Install Starplot:
```
pip install starplot
```

3. Install Shapely:
```
pip uninstall -y shapely
pip install --no-binary :all: shapely
```

## Linux (debian)

1. Install required system libraries: 
```
apt-get install libgeos-dev libgdal-dev
```

2. Install Starplot:
```
pip install starplot
```

3. Install Shapely:
```
pip uninstall -y shapely
pip install --no-binary :all: shapely
```
