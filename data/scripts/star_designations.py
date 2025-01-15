import csv

import pandas as pd
import pyarrow as pa
import numpy as np

from settings import RAW_PATH, BUILD_PATH

star_records = []

with open(RAW_PATH / "star_designations.csv", "r") as csvfile:
    reader = csv.DictReader(csvfile)

    for row in reader:
        star = row.copy()
        star["hip"] = int(star["hip"])
        # star["flamsteed"] = int(star["flamsteed"]) if star.get("flamsteed") else None
        star_records.append(star)

df = pd.DataFrame.from_records(star_records)

schema = pa.schema(
    [
        ("hip", pa.int32()),
        ("name", pa.string()),
        ("bayer", pa.string()),
        ("flamsteed", pa.string()),
    ]
)

df.to_parquet(
    BUILD_PATH / "star_designations.parquet",
    engine="pyarrow",
    schema=schema,
    compression="none",
)

print("Star Designations: " + str(len(star_records)))
