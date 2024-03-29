import os
from pathlib import Path

import geopandas as gpd
import pandas as pd

from shapely.geometry import Polygon, MultiPolygon, Point

from starplot.data import constellations

HERE = Path(__file__).resolve().parent
DATA_PATH = HERE.parent / "raw" / "iau"

CRS = "+ellps=sphere +f=0 +proj=latlong +axis=wnu +a=6378137 +no_defs"

# - Three letter (index)
# - Full name
# - Centroid
# - Min bounding box of lines
# - Polygon of bounds
# - List of HIP ids for lines

# constellation_dict = {
#     "id": [],
#     "name": [],
#     "centroid": [],
#     "lines_bounding_box": [],
#     "lines_hip_ids": [],
#     "borders": [],
# }

# 09 42 50.2171| 41.4316750|UMA


def parse_ra(ra_str):
    """Parses RA from border file HH MM SS to 0...360 degree float"""
    h, m, s = ra_str.strip().split(" ")
    return 15 * (float(h) + float(m) / 60 + float(s) / 3600)


def parse_dec(dec_str):
    """Parses DEC from ONGC CSV from HH:MM:SS to -90...90 degree float"""
    return float(dec_str)


def parse_borders(lines):
    coords = []
    for line in lines:
        if "|" not in line:
            continue
        ra_str, dec_str, cid = line.split("|")
        ra = parse_ra(ra_str)
        dec = parse_dec(dec_str)
        coords.append((ra, dec))
    return coords


constellation_records = []


con_ids = constellations.properties
con_lines = constellations.lines()


for cid, props in constellations.properties.items():
    constellation_dict = {
        "id": cid.lower(),
        "name": props[0],
        "center_ra": props[1] * 15,
        "center_dec": props[2],
        "lines_hip_ids": ",".join(
            "-".join([str(h) for h in hips]) for hips in con_lines[cid.lower()]
        ),
    }
    print(cid)

    if cid == "Ser":
        ser1_coords = []
        ser2_coords = []
        with open(DATA_PATH / "ser1.txt", "r") as ser1:
            ser1_coords = parse_borders(ser1.readlines())

        with open(DATA_PATH / "ser2.txt", "r") as ser2:
            ser2_coords = parse_borders(ser2.readlines())

        constellation_dict["geometry"] = MultiPolygon(
            [Polygon(ser1_coords), Polygon(ser2_coords)]
        )

    else:
        with open(DATA_PATH / f"{cid.lower()}.txt", "r") as borderfile:
            coords = parse_borders(borderfile.readlines())
            constellation_dict["geometry"] = Polygon(coords)

    constellation_records.append(constellation_dict)


df = pd.DataFrame.from_records(constellation_records)

gdf = gpd.GeoDataFrame(
    df,
    geometry=df["geometry"],
    crs=CRS,
)
gdf = gdf.set_index("id")
gdf.to_file("build/constellations.gpkg", driver="GPKG", crs=CRS, index=True)

print(gdf.loc["uma"])

print("Total: " + str(len(constellation_records)))
# result = gpd.read_file(HERE.parent / "build" / "ngc.gpkg")
# print(result)
