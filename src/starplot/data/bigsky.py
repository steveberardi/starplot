import os
from pathlib import Path

import pandas as pd

from starplot import settings
from starplot.data import DataFiles, utils


BIG_SKY_VERSION = "0.4.0"
BIG_SKY_FILENAME = f"bigsky.{BIG_SKY_VERSION}.stars.csv.gz"
BIG_SKY_PQ_FILENAME = f"bigsky.{BIG_SKY_VERSION}.stars.parquet"

BIG_SKY_MAG11_FILENAME = f"bigsky.{BIG_SKY_VERSION}.stars.mag11.csv.gz"
BIG_SKY_MAG11_PQ_FILENAME = f"bigsky.{BIG_SKY_VERSION}.stars.mag11.parquet"


def get_url(version: str = BIG_SKY_VERSION, filename: str = BIG_SKY_FILENAME):
    return f"https://github.com/steveberardi/bigsky/releases/download/v{version}/{filename}"


def download(
    url: str = None,
    download_path: str = settings.DOWNLOAD_PATH,
    download_filename: str = BIG_SKY_FILENAME,
    build_file: str = DataFiles.BIG_SKY,
):
    url = url or get_url()
    download_path = Path(download_path)

    if not os.path.exists(download_path):
        os.makedirs(download_path)

    full_download_path = download_path / download_filename
    utils.download(
        url,
        full_download_path,
        "Big Sky Star Catalog",
    )
    to_parquet(
        full_download_path,
        build_file,
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


def download_if_not_exists(
    filename: str = DataFiles.BIG_SKY,
    url: str = None,
    download_path: str = settings.DOWNLOAD_PATH,
    download_filename: str = BIG_SKY_FILENAME,
    build_file: str = DataFiles.BIG_SKY,
):
    if not exists(filename):
        download(
            url=url,
            download_path=download_path,
            download_filename=download_filename,
            build_file=build_file,
        )
