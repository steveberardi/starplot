Starplot is available on [PyPI](https://pypi.org/project/starplot/), but it's basically just a thin layer on top of Matplotlib, Skyfield, Cartopy, and others. So, before installing Starplot you'll need a few dependencies:

```
pip install starplot
```

## Required Dependencies

- GEOS
- GDAL
- Shapely


## macOS
```shell
brew install geos gdal

pip install starplot
pip uninstall -y shapely
pip install --no-binary :all: shapely

```

## Linux (debian)

```shell
apt-get install libgeos-dev libgdal-dev

pip install starplot
pip uninstall -y shapely
pip install --no-binary :all: shapely

```