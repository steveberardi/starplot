import csv
from pathlib import Path

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from shapely.geometry import Point

"""
    This script creates a smaller parquet file with stars from Big Sky Mag 11

    Set limit to limiting magnitude of destination file
"""

HERE = Path(__file__).resolve().parent
DATA_PATH = HERE.parent / "raw"

CRS = "+ellps=sphere +f=0 +proj=latlong +axis=wnu +a=6378137 +no_defs"

BIGSKY_VERSION = "0.4.0"

limit = 9
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

        values = {
            k: parse(v)
            for k, v in row.items()
            if k not in ["name", "bayer", "flamsteed", "hd_id"]
        }
        star_records.append(
            {
                **values,
                "hip": hip_id,
                "ra_degrees": ra,
                "dec_degrees": dec,
                # "geometry": Point(ra, dec),
            }
        )


df = pd.DataFrame.from_records(star_records)

df = df[df["magnitude"] <= limit]
df = df.sort_values(["magnitude"])

table = pa.Table.from_pandas(df)
table = table.drop_columns("__index_level_0__")

print(table.column_names)

pq.write_table(
    table,
    f"temp/stars.bigsky.{BIGSKY_VERSION}.mag{str(limit)}.parquet",
    compression="snappy",
    # use_dictionary=True,
    # row_group_size=10_000,
    sorting_columns=[
        pq.SortingColumn(2),
        # pq.SortingColumn(df.columns.get_loc('ra')),
    ],
)


print(df)

print("Total: " + str(len(df)))
