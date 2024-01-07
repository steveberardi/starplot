"""Converts GeoJSON to GeoPackage"""

import geopandas as gpd

from starplot.data import DataFiles

constellation_borders = gpd.read_file(DataFiles.CONSTELLATION_BORDERS.value)
constellation_borders.to_file("temp/constellation_borders.gpkg", driver="GPKG")

constellation_lines = gpd.read_file(DataFiles.CONSTELLATION_LINES.value)
constellation_lines.to_file("temp/constellation_lines.gpkg", driver="GPKG")

milkyway = gpd.read_file(DataFiles.MILKY_WAY.value)
milkyway.to_file("temp/milkyway.gpkg", driver="GPKG")
