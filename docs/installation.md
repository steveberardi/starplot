Starplot is available on [PyPI](https://pypi.org/project/starplot/), but it's basically just a thin layer on top of Matplotlib, Skyfield, Cartopy, and others. So, before installing Starplot you'll need a few dependencies. Below are instructions for installing on macOS and Linux.

Supported Python versions: 3.9+

## Required Dependencies

- GEOS
- GDAL

## macOS

1. **Install required system libraries (via [Homebrew](https://brew.sh/)):**
```
brew install geos gdal
```

2. **Install Starplot:**
```
pip install starplot
```

## Linux (debian)

1. **Install required system libraries:**
```
apt-get install libgeos-dev libgdal-dev
```

2. **Install Starplot:**
```
pip install starplot
```

!!! note "What about Windows?"

    I haven't tried installing Starplot on Windows, but if you have and would like to share instructions, please feel free to [open a pull request on GitHub](https://github.com/steveberardi/starplot) with an update to this file (`docs/installation.md`). Thanks! :)

---

## Troubleshooting

### Segmentation Fault with map plots

If you're seeing "segmentation fault" errors when creating map plots, you may have to install [shapely](https://shapely.readthedocs.io/en/stable/index.html) from source for your runtime environment:
```
pip install --no-binary :all: shapely
```
*Warning: this may take awhile (5+ minutes), because it builds shapely from source.*
