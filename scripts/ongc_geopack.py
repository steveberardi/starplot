import os
from pathlib import Path

import geopandas as gpd
import pandas as pd

from shapely.geometry import Polygon, MultiPolygon


HERE = Path(__file__).resolve().parent
DATA_PATH = HERE.parent / "raw" / "ongc" / "outlines"

CRS = "+ellps=sphere +f=0 +proj=latlong +axis=wnu +a=6378137 +no_defs"
IGNORE_OUTLINES = [
    "IC0424",  # seems too big?
]
MIN_SIZE = 0.1


def read_csv():
    df = pd.read_csv(
        "raw/ongc/NGC.csv",
        sep=";",
    )
    df_addendum = pd.read_csv(
        "raw/ongc/addendum.csv",
        sep=";",
    )
    df = pd.concat([df, df_addendum])
    df["ra_degrees"] = df.apply(parse_ra, axis=1)
    df["dec_degrees"] = df.apply(parse_dec, axis=1)

    gdf = gpd.GeoDataFrame(
        df,
        geometry=gpd.points_from_xy(df.ra_degrees, df.dec_degrees),
        crs=CRS,
    )

    gdf.to_file("build/ngc.base.gpkg", driver="GPKG", crs=CRS)

    return gdf


def parse_ra(row):
    """Parses RA from ONGC CSV from HH:MM:SS to 0...360 degree float"""
    if row.Type == "NonEx":
        print(f"Non Existent object, ignoring... {row.Name}")
        return
    try:
        ra = row.RA
        h, m, s = ra.split(":")
        return 15 * (float(h) + float(m) / 60 + float(s) / 3600)
    except Exception as e:
        print(row.Name)
        return None


def parse_dec(row):
    """Parses DEC from ONGC CSV from HH:MM:SS to -90...90 degree float"""
    if row.Type == "NonEx":
        print(f"Non Existent object, ignoring... {row.Name}")
        return
    try:
        dec = row.Dec
        if dec[0] == "-":
            mx = -1
        else:
            mx = 1
        h, m, s = dec[1:].split(":")
        return mx * (float(h) + float(m) / 60 + float(s) / 3600)
    except Exception as e:
        print(row.Name)
        return None


def parse_designation_from_filename(filename):
    designation, level = filename.split("_")

    if designation.startswith("IC"):
        ic = designation[2:]
    else:
        ic = None

    if designation.startswith("NGC"):
        ngc = designation[3:]
    else:
        ngc = None

    return designation, ic, ngc, level


def walk_files(path=DATA_PATH):
    for dirpath, dirnames, filenames in os.walk(path):
        for filename in sorted(filenames):
            yield Path(os.path.join(dirpath, filename))


gdf = read_csv()
gdf = gdf.set_index("Name")

outlines = {}

for f in walk_files():
    designation, ic, ngc, level = parse_designation_from_filename(f.name)
    name, _ = f.name.split("_")

    if level == "lv3" or name in IGNORE_OUTLINES:
        continue
    # if designation in d['designation']:
    #     continue

    dso_df = pd.read_csv(f, sep="\t")
    polygons = []
    current_poly = []

    for i, row in dso_df.iterrows():
        cont_flag = row["Cont_Flag"]
        ra = row["RAJ2000"]
        dec = row["DEJ2000"]
        current_poly.append([ra, dec])

        if cont_flag == "*":
            # a * indicates this is the last point in the current polygon
            polygons.append(current_poly)
            current_poly = []

    if len(polygons) > 1:
        dso_geom = MultiPolygon([Polygon(p) for p in polygons])
    else:
        dso_geom = Polygon(polygons[0])

    if dso_geom.area > MIN_SIZE:
        outlines[designation] = dso_geom

    if not ic and not ngc:
        print(designation)
        centroid = dso_geom.centroid
        gdf.loc[name, "geometry"] = dso_geom
        gdf.loc[name, "ra_degrees"] = centroid.x
        gdf.loc[name, "dec_degrees"] = centroid.y
        gdf.loc[name, "Type"] = "Neb"
    else:
        if gdf.loc[name].empty:
            print(f"NGC/IC object not found: {name}")
        elif dso_geom.area > MIN_SIZE:
            gdf.loc[name, "geometry"] = dso_geom


gdf_outlines = gpd.GeoDataFrame(
    {"designation": outlines.keys(), "geometry": outlines.values()}
)

print(gdf.loc["Orion"])
gdf.to_file(HERE.parent / "build" / "ngc.gpkg", driver="GPKG", crs=CRS, index=True)
gdf_outlines.to_file(
    HERE.parent / "build" / "nebulae.gpkg", driver="GPKG", crs=CRS, index=True
)

print("Total: " + str(len(outlines)))
# result = gpd.read_file(HERE.parent / "build" / "ngc.gpkg")
# print(result)
