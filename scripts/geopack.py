"""Converts GeoJSON to GeoPackage"""
import geopandas as gpd
import pandas as pd

from shapely.geometry import Polygon


from starplot.data import DataFiles

# constellation_borders = gpd.read_file(DataFiles.CONSTELLATION_BORDERS.value)
constellation_borders = gpd.read_file("raw/i.constellations.borders.json")
constellation_borders.to_file("build/constellation_borders.gpkg", driver="GPKG")

# constellation_lines = gpd.read_file(DataFiles.CONSTELLATION_LINES.value)
# print(constellation_lines.has_sindex)
# constellation_lines.sindex
# constellation_lines.to_file("temp/constellation_lines.gpkg", driver="GPKG")

# milkyway = gpd.read_file(DataFiles.MILKY_WAY.value)
# milkyway.to_file("temp/milkyway.gpkg", driver="GPKG")

# milkyway = gpd.read_file("temp/mwayz.json")
# milkyway.to_file("temp/mwayz.gpkg", driver="GPKG")


# Read outline file
# df = pd.read_csv("temp/NGC1499_lv1.txt", sep="\t")
# print(df)

# # Create shapely polygon
# polygon_geom = Polygon(zip(df["RAJ2000"], df["DEJ2000"]))

# # Create GeoDataFrame
# polygon = gpd.GeoDataFrame(index=[0], geometry=[polygon_geom])

# # Simplify and write to file
# polygon.simplify(10)
# polygon.to_file("temp/canebula.gpkg", driver="GPKG", compression="zip")
