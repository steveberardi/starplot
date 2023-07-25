

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