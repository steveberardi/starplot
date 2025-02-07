Starplot is available on [PyPI](https://pypi.org/project/starplot/), and its dependencies have binary wheels for most operating systems, so installation should be easy via pip. See below for details.

Supported Python versions: 3.10 / 3.11 / 3.12

## macOS / Linux

1. **Install Starplot:**
```
pip install starplot
```

2. (optional) **Setup Starplot:**
```
starplot setup --install-big-sky
```
This will install the required [spatial extension](https://duckdb.org/docs/extensions/spatial/overview.html) for DuckDB, build the matplotlib font cache, and download the full Big Sky catalog. Starplot will do this automatically, but this `setup` command is a way to do it ahead of time (useful for deployed environments, continuous integration, etc). You can control where Starplot stores these files via [environment variables](reference-settings.md).

## Docker

Here's a basic Docker container definition that'll get you up and running:

```docker
FROM python:3.11.11-bookworm

RUN pip install starplot
RUN starplot setup --install-big-sky  # Optional
```

!!! star "What about Windows?"

    I haven't tried installing Starplot on Windows, but if you have and would like to share instructions, please feel free to [open a pull request on GitHub](https://github.com/steveberardi/starplot) with an update to this file (`docs/installation.md`). Thanks! :)

---

## Troubleshooting

### GEOS / GDAL errors on installation

If you see any errors related to GEOS and/or GDAL when trying to install Starplot, then you may need to build those dependencies from source for your environment.

See their websites for details:

- [GEOS](https://libgeos.org/)
- [GDAL](https://gdal.org/)

### Segmentation Fault with map plots

If you're seeing "segmentation fault" errors when creating map plots, you may have to install [shapely](https://shapely.readthedocs.io/en/stable/index.html) from source for your runtime environment:
```
pip install --no-binary :all: shapely
```
*Warning: this may take awhile (5+ minutes), because it builds shapely from source.*


<br/><br/><br/>
