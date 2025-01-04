import csv
from pathlib import Path

import geopandas as gpd
import pandas as pd

from shapely.geometry import Point

HERE = Path(__file__).resolve().parent
DATA_PATH = HERE.parent / "raw"

CRS = "+ellps=sphere +f=0 +proj=latlong +axis=wnu +a=6378137 +no_defs"

BIGSKY_VERSION = "0.3.0"

star_records = []


def parse(value):
    try:
        return float(value)
    except ValueError:
        return value if value else None


with open(DATA_PATH / f"bigsky.{BIGSKY_VERSION}.stars.mag11.csv", "r") as bigsky_file:
    reader = csv.DictReader(bigsky_file)
    for row in reader:
        ra = float(row.pop("ra_degrees_j2000"))
        dec = float(row.pop("dec_degrees_j2000"))
        hip_id = row.pop("hip_id")
        hip_id = int(hip_id) if hip_id else 0

        values = {k: parse(v) for k, v in row.items()}
        star_records.append(
            {
                **values,
                "hip_id": hip_id,
                "ra": ra,
                "dec": dec,
                "geometry": Point(ra, dec),
            }
        )


df = pd.DataFrame.from_records(star_records)
gdf = gpd.GeoDataFrame(
    df,
    geometry=df["geometry"],
    # crs=CRS,
)
gdf.to_file("temp/stars.gpkg", driver="GPKG", crs=CRS, index=True)
gdf.to_parquet("temp/stars.parquet", index=True)  # , geometry_encoding="geoarrow")

print(gdf)

print("Total: " + str(len(star_records)))
