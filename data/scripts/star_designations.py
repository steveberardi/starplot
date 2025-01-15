import csv

import pandas as pd
import pyarrow as pa
import numpy as np

from settings import RAW_PATH, BUILD_PATH

star_records = []

with open(RAW_PATH / "star_designations.csv", "r") as csvfile:
    reader = csv.DictReader(csvfile)
    star_records = [row for row in reader]
    # TODO : cast to ints


df = pd.DataFrame.from_records(star_records)


df = df.astype({"hip": "int32"})

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

print("Total: " + str(len(star_records)))
