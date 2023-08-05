Starplot is available on [PyPI](https://pypi.org/project/starplot/), but it's basically just a thin layer on top of Matplotlib, Skyfield, Cartopy, and others. So, before installing Starplot you'll need a few dependencies. Below are instructions for installing on macOS and Linux.

!!! tip "Docker Base Image Available"

    Installing the base dependencies for Starplot can take awhile (10+ minutes), so I've created a base Docker image that has some of these dependencies compiled already which saves a lot of time. The image is available on [Docker Hub](https://hub.docker.com/r/sberardi/starplot-base).

## Required Dependencies

- GEOS
- GDAL
- Shapely

## macOS

1. **Install required system libraries (via [Homebrew](https://brew.sh/)):**
```
brew install geos gdal
```

2. **Install Shapely:**
```
pip install --no-binary :all: shapely
```
*Warning: this step may take awhile (5+ minutes), because it builds shapely from source.*

3. **Install Starplot:**
```
pip install starplot
```

## Linux (debian)

1. **Install required system libraries:**
```
apt-get install libgeos-dev libgdal-dev
```

2. **Install Shapely:**
```
pip install --no-binary :all: shapely
```
*Warning: this step may take awhile (5+ minutes), because it builds shapely from source.*

3. **Install Starplot:**
```
pip install starplot
```

---

!!! note "What about Windows?"

    I haven't tried installing Starplot on Windows, but if you have and would like to share instructions, please feel free to [open a pull request on GitHub](https://github.com/steveberardi/starplot) with an update to this file (`docs/installation.md`). Thanks! :)
