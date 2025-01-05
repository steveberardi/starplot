import os

import pandas as pd

from starplot.data import DATA_PATH, DOWNLOAD_PATH, DataFiles, utils


BIG_SKY_VERSION = "0.4.0"
BIG_SKY_FILENAME = f"bigsky.{BIG_SKY_VERSION}.stars.csv.gz"
BIG_SKY_PQ_FILENAME = f"bigsky.{BIG_SKY_VERSION}.stars.parquet"
BIG_SKY_URL = f"https://github.com/steveberardi/bigsky/releases/download/v{BIG_SKY_VERSION}/{BIG_SKY_FILENAME}"

DIGITS = 4


def download(
    download_path: str = None,
    digits: int = 4,
):
    download_path = download_path or str(DOWNLOAD_PATH / BIG_SKY_FILENAME)
    utils.download(
        BIG_SKY_URL,
        download_path,
        "Big Sky Star Catalog",
    )
    to_parquet(
        download_path,
        DataFiles.BIG_SKY,
        digits,
    )


def to_parquet(source_path: str, destination_path: str, digits: int = DIGITS):
    import pyarrow as pa

    print("Preparing Big Sky Catalog for Starplot...")

    df = pd.read_csv(
        source_path,
        header=0,
        names=[
            "tyc_id",
            "hip_id",
            "ccdm",
            "magnitude",
            "bv",
            "ra_degrees_j2000",
            "dec_degrees_j2000",
            "ra_mas_per_year",
            "dec_mas_per_year",
            "parallax_mas",
        ],
        compression="gzip",
    )

    schema = pa.schema(
        [
            ("tyc_id", pa.string()),
            ("hip_id", pa.int32()),
            ("ccdm", pa.string()),
            ("magnitude", pa.float16()),
            ("bv", pa.float16()),
            ("ra_degrees_j2000", pa.float16()),
            ("dec_degrees_j2000", pa.float16()),
            ("ra_mas_per_year", pa.float16()),
            ("dec_mas_per_year", pa.float16()),
            ("parallax_mas", pa.float16()),
        ]
    )

    df.to_parquet(destination_path, engine="pyarrow", schema=schema, compression="gzip")

    print(f"Done! {destination_path}")


def exists(path) -> bool:
    return os.path.isfile(path)


def download_if_not_exists():
    if not exists(DOWNLOAD_PATH / BIG_SKY_FILENAME):
        download()
