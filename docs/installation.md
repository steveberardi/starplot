Starplot is available on [PyPI](https://pypi.org/project/starplot/), but it's basically just a thin layer on top of [Matplotlib](https://matplotlib.org/stable/), [Skyfield](https://github.com/skyfielders/python-skyfield), [Cartopy](https://scitools.org.uk/cartopy/docs/latest/), and others. So, before installing Starplot you'll need a few dependencies. Below are instructions for installing on macOS and Linux.

Supported Python versions: 3.10 / 3.11 / 3.12

Required Dependencies: [GEOS](https://libgeos.org/), [GDAL](https://gdal.org/)

## macOS / Linux (debian)

1. **Install required system libraries**

    macOS (via [Homebrew](https://brew.sh/)):
    ```
    brew install geos gdal
    ```

    Linux (debian):
    ```
    apt-get install libgeos-dev libgdal-dev
    ```

2. **Install Starplot:**
```
pip install starplot
```

3. (optional) **Setup Starplot:**
```
starplot setup --install-big-sky
```
This will install the required [spatial extension](https://duckdb.org/docs/extensions/spatial/overview.html) for DuckDB, build the matplotlib font cache, and download the full Big Sky catalog. Starplot will do this automatically, but this `setup` command is a way to do it ahead of time (useful for deployed environments, continuous integration, etc). You can control where Starplot stores these files via [environment variables](reference-settings.md).

## Docker

Here's a basic Docker container definition that'll get you up and running:

```docker
FROM python:3.11.11-bookworm

# Install required system libraries (GEOS + GDAL)
RUN apt-get clean && apt-get update -y && apt-get install -y libgeos-dev libgdal-dev

RUN pip install starplot
RUN starplot setup --install-big-sky  # Optional
```

!!! star "What about Windows?"

    I haven't tried installing Starplot on Windows, but if you have and would like to share instructions, please feel free to [open a pull request on GitHub](https://github.com/steveberardi/starplot) with an update to this file (`docs/installation.md`). Thanks! :)

---

## Troubleshooting

### Segmentation Fault with map plots

If you're seeing "segmentation fault" errors when creating map plots, you may have to install [shapely](https://shapely.readthedocs.io/en/stable/index.html) from source for your runtime environment:
```
pip install --no-binary :all: shapely
```
*Warning: this may take awhile (5+ minutes), because it builds shapely from source.*
