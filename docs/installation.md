Starplot is available on [PyPI](https://pypi.org/project/starplot/), and its dependencies have binary wheels for most operating systems, so installation should be easy via pip. See below for details.

Supported Python versions: 3.10 / 3.11 / 3.12 / 3.13


<h3>1. Install Starplot</h3>
```
pip install starplot
```

<h3>2. Setup Starplot (optional)</h3>
```
starplot setup --install-big-sky
```
This will install the required [spatial extension](https://duckdb.org/docs/stable/core_extensions/spatial/overview.html) for DuckDB, build the matplotlib font cache, and download the full Big Sky catalog. Starplot will do this automatically, but this `setup` command is a way to do it ahead of time (useful for deployed environments, continuous integration, etc). You can control where Starplot stores these files via [environment variables](reference-settings.md).


---

## Troubleshooting

### GEOS / GDAL errors on installation

If you see any errors related to GEOS and/or GDAL when trying to install Starplot, then you may need to build those dependencies from source for your environment.

See their websites for details:

- [GEOS](https://libgeos.org/)
- [GDAL](https://gdal.org/)

### Segmentation Faults

If you're seeing "segmentation fault" errors when creating maps, you may have to install [shapely](https://shapely.readthedocs.io/en/stable/index.html) from source for your runtime environment:
```
pip install --no-binary :all: shapely
```
*Warning: this may take awhile (5+ minutes), because it builds shapely from source.*

### Other Issues

If you experience another problem, then please [open an issue on our GitHub page](https://github.com/steveberardi/starplot/issues) and include the following information: operating system (and version), Python version, Starplot version, and Matplotlib version.

<br/><br/><br/>
