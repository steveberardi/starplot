from pathlib import Path

import pandas as pd
import pyarrow as pa

from starplot.data import bayer, flamsteed, stars

HERE = Path(__file__).resolve().parent
DATA_PATH = HERE.parent / "raw" / "iau"


hips = list(
    set().union(bayer.hip.keys(), flamsteed.hip.keys(), stars.STAR_NAMES.keys())
)
hips.sort()

star_records = [
    {
        "hip": hip_id,
        "name": stars.STAR_NAMES.get(hip_id),
        "bayer": bayer.hip.get(hip_id),
        "flamsteed": flamsteed.hip.get(hip_id),
    }
    for hip_id in hips
]


df = pd.DataFrame.from_records(star_records)

df.set_index("hip")

schema = pa.schema(
    [
        ("hip", pa.int32()),
        ("name", pa.string()),
        ("bayer", pa.string()),
        ("flamsteed", pa.int32()),
    ]
)

df.to_csv("temp/star_designations.csv")
df.to_parquet(
    "temp/star_designations.parquet",
    engine="pyarrow",
    schema=schema,
    compression="gzip",
)


print("Total: " + str(len(star_records)))
