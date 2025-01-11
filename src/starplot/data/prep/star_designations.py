from pathlib import Path

import pandas as pd
import pyarrow as pa

from starplot import settings
from starplot.data import bayer, flamsteed, stars

DATA_PATH = settings.RAW_DATA_PATH / "iau"

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

df.to_parquet(
    settings.BUILD_PATH / "star_designations.parquet",
    engine="pyarrow",
    schema=schema,
    compression="snappy",
)


print("Total: " + str(len(star_records)))
