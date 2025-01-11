import os
import zipfile
from pathlib import Path

import geopandas as gpd
import pandas as pd
import numpy as np

from shapely.geometry import Polygon, MultiPolygon
from starplot import geod

HERE = Path(__file__).resolve().parent
DATA_PATH = HERE.parent / "raw" / "ongc" / "outlines"
BUILD_PATH = HERE.parent / "build"

CRS = "+ellps=sphere +f=0 +proj=latlong +axis=wnu +a=6378137 +no_defs"
IGNORE_OUTLINES = [
    "IC0424",  # seems too big?
]
MIN_SIZE = 0.1


def _size(d):
    """Returns size (in sq degrees) of minimum bounding rectangle of a DSO"""
    size = None
    geometry_types = d["geometry"].geom_type

    if "Polygon" in geometry_types and "MultiPolygon" not in geometry_types:
        size = d.geometry.envelope.area

    elif "MultiPolygon" in geometry_types:
        size = sum([p.envelope.area for p in d.geometry.geoms])

    elif d.maj_ax and not np.isnan(d.min_ax):
        size = (d.maj_ax / 60) * (d.min_ax / 60)

    elif d.maj_ax:
        size = (d.maj_ax / 60) ** 2

    if size:
        size = round(size, 8)

    return size


COLUMN_MAP = {
    "Name": "name",
    "Type": "type",
    "RA": "ra",
    "Dec": "dec",
    "M": "m",
    "NGC": "ngc",
    "IC": "ic",
    "MajAx": "maj_ax",
    "MinAx": "min_ax",
    "PosAng": "angle",
    "B-Mag": "mag_b",
    "V-Mag": "mag_v",
    "Common names": "common_names",
    "Const": "constellation",
}
"""Input name -> output name"""


def read_csv():
    df = pd.read_csv(
        "raw/ongc/NGC.csv",
        sep=";",
        usecols=COLUMN_MAP.keys(),
    )
    df_addendum = pd.read_csv(
        "raw/ongc/addendum.csv",
        sep=";",
        usecols=COLUMN_MAP.keys(),
    )
    df = pd.concat([df, df_addendum])
    df["ra_degrees"] = df.apply(parse_ra, axis=1)
    df["dec_degrees"] = df.apply(parse_dec, axis=1)

    df["M"] = df.apply(parse_m, axis=1)
    df["IC"] = df.apply(parse_ic, axis=1)
    df["NGC"] = df.apply(parse_ngc, axis=1)

    df["Const"] = df.apply(lambda d: str(d.Const).lower(), axis=1)

    df.drop("RA", axis=1, inplace=True)
    df.drop("Dec", axis=1, inplace=True)

    df = df.rename(columns=COLUMN_MAP)

    gdf = gpd.GeoDataFrame(
        df,
        geometry=gpd.points_from_xy(df.ra_degrees, df.dec_degrees),
        crs=CRS,
    )

    gdf.to_file("build/ngc.base.gpkg", driver="GPKG", crs=CRS)

    return gdf


def parse_m(row):
    """Parses messier number"""
    if not np.isnan(row.M):
        return str(int(row.M)).lstrip("0")

    return None


def parse_ic(row):
    """Parses IC number if name starts with IC"""
    if row.Name.startswith("IC"):
        return row.Name[2:].lstrip("0")

    if str(row.IC) != "nan":
        return str(row.IC).lstrip("0")

    return None


def parse_ngc(row):
    """Parses NGC number if name starts with NGC"""
    if row.Name.startswith("NGC"):
        return row.Name[3:].lstrip("0")

    if str(row.NGC) != "nan":
        return str(row.NGC).lstrip("0")

    return None


def parse_ra(row):
    """Parses RA from ONGC CSV from HH:MM:SS to 0...360 degree float"""
    if row.Type == "NonEx":
        print(f"Non Existent object, ignoring... {row.Name}")
        return
    try:
        ra = row.RA
        h, m, s = ra.split(":")
        return round(15 * (float(h) + float(m) / 60 + float(s) / 3600), 4)
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
        return round(mx * (float(h) + float(m) / 60 + float(s) / 3600), 4)
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


def create_ellipse(d):
    maj_ax, min_ax, angle = d.maj_ax, d.min_ax, d.angle

    if str(d.geometry.geom_type) in ["Polygon", "MultiPolygon"]:
        return d.geometry

    if np.isnan(maj_ax):
        return d.geometry

    if np.isnan(angle):
        angle = 0

    maj_ax_degrees = (maj_ax / 60) / 2

    if np.isnan(min_ax):
        min_ax_degrees = maj_ax_degrees
    else:
        min_ax_degrees = (min_ax / 60) / 2

    points = geod.ellipse(
        (d.ra_degrees, d.dec_degrees),
        min_ax_degrees * 2,
        maj_ax_degrees * 2,
        angle,
        num_pts=100,
    )

    def fix_ra(r):
        if r < 0:
            r += 360
        return round(r, 4)

    points = [(fix_ra(ra), round(dec, 4)) for ra, dec in points]

    return Polygon(points)


gdf = read_csv()
gdf = gdf.set_index("name")

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
        gdf.loc[name, "type"] = "Neb"
    else:
        if gdf.loc[name].empty:
            print(f"NGC/IC object not found: {name}")
        elif dso_geom.area > MIN_SIZE:
            gdf.loc[name, "geometry"] = dso_geom

# add size column
gdf["size_deg2"] = gdf.apply(_size, axis=1)


gdf["geometry"] = gdf.apply(create_ellipse, axis=1)


print(gdf.loc["NGC2168"])  # M35

print(gdf.loc["NGC6705"])  # M11


gdf.to_file("temp/ongc.gpkg", driver="GPKG", crs=CRS, index=True)


print("Total nebula outlines: " + str(len(outlines)))
# result = gpd.read_file(HERE.parent / "build" / "ngc.gpkg")
# print(result)

# Zip it up!
zipped = zipfile.ZipFile(BUILD_PATH / "ongc.gpkg.zip", "w", zipfile.ZIP_DEFLATED)
zipped.write(BUILD_PATH / "ongc.gpkg")
zipped.close()
