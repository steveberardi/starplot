"""Converts GeoJSON to GeoPackage"""
import geopandas as gpd
import pandas as pd

import json

from shapely.geometry import Polygon


from starplot.data import DataFiles

constellation_borders = gpd.read_file(DataFiles.CONSTELLATION_BORDERS)
# constellation_borders = gpd.read_file("raw/i.constellations.borders.json")
# constellation_borders.to_file("build/constellation_borders.gpkg", driver="GPKG")


geo_json = None

with open("temp/constellation_borders.json", "r") as infile:
    data = infile.read()
    geo_json = json.loads(data)

new_json = geo_json.copy()
new_lines = []


def lon_to_ra(lon: float):
    pos_lon = lon + 180
    ra = 12 - (24 * pos_lon / 360)
    if ra < 0:
        ra += 24
    return ra


for feature in geo_json.get("features"):
    geometry = feature.get("geometry")
    ctr = 0
    for line in geometry["coordinates"]:
        ctr += 1
        new_line = []
        for x, y in line:
            # if x < 0:
            #     x += 360
            x = lon_to_ra(x) * 15
            new_line.append([x, y])
        new_lines.append(new_line)

    # print("lines = " + str(ctr))


new_json["features"] = []

for line in new_lines:
    new_json["features"].append(
        {
            "type": "Feature",
            "properties": {},
            "geometry": {
                "type": "LineString",
                "coordinates": line,
            },
        }
    )

with open("temp/constellation_borders_new_temp.json", "w") as outfile:
    outfile.write(json.dumps(new_json))


constellation_borders = gpd.read_file("temp/constellation_borders_new_temp.json")

constellation_borders.to_file("temp/constellation_borders_new.json", driver="GeoJSON")

# constellation_borders["geometry"] = constellation_borders["geometry"].transform(fix_ra)


# constellation_borders.to_file(
#     "temp/constellation_borders.json", driver="GeoJSON"
# )

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
