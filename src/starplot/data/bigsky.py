import os

import pandas as pd

from starplot.data import DATA_PATH, DOWNLOAD_PATH, DataFiles, utils


BIG_SKY_VERSION = "0.4.0"
BIG_SKY_FILENAME = f"bigsky.{BIG_SKY_VERSION}.stars.csv.gz"
BIG_SKY_PQ_FILENAME = f"bigsky.{BIG_SKY_VERSION}.stars.parquet"
BIG_SKY_URL = f"https://github.com/steveberardi/bigsky/releases/download/v{BIG_SKY_VERSION}/{BIG_SKY_FILENAME}"

DIGITS = 4


def download(
    download_path: str = str(DOWNLOAD_PATH / BIG_SKY_FILENAME),
    digits: int = 4,
):
    utils.download(
        BIG_SKY_URL,
        download_path,
        "Big Sky Star Catalog",
    )
    to_parquet(
        download_path,
        DataFiles.BIG_SKY,
    )


def to_parquet(source_path: str, destination_path: str):
    import pyarrow as pa
    import pyarrow.parquet as pq

    print("Preparing Big Sky Catalog for Starplot...")

    df = pd.read_csv(
        source_path,
        header=0,
        usecols=[
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
            "constellation",
        ],
        compression="gzip",
    )

    df = df.assign(epoch_year=2000)

    df = df.rename(
        columns={
            "hip_id": "hip",
            "ra_degrees_j2000": "ra_degrees",
            "dec_degrees_j2000": "dec_degrees",
        }
    )

    df = df.sort_values(["magnitude"])

    table = pa.Table.from_pandas(df)
    table = table.drop_columns("__index_level_0__")

    pq.write_table(
        table,
        destination_path,
        compression="none",
        sorting_columns=[
            pq.SortingColumn(df.columns.get_loc("magnitude")),
        ],
    )

    print(f"Done! {destination_path}")


def exists(path) -> bool:
    return os.path.isfile(path)


def download_if_not_exists():
    if not exists(DOWNLOAD_PATH / BIG_SKY_FILENAME):
        download()
