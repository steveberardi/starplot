import os

import pandas as pd

from starplot.data import DATA_PATH, DataFiles, utils


BIG_SKY_VERSION = "0.1.0"

BIG_SKY_FILENAME = "bigsky.stars.csv.gz"

BIG_SKY_URL = f"https://github.com/steveberardi/bigsky/releases/download/v{BIG_SKY_VERSION}/{BIG_SKY_FILENAME}"

DOWNLOADED_PATH = DATA_PATH / BIG_SKY_FILENAME

DIGITS = 4

BIG_SKY_ASSETS = {
    DataFiles.BIG_SKY: "bigsky.stars.csv.gz",
    DataFiles.BIG_SKY_MAG11: "bigsky.stars.mag11.csv.gz",
}


def url(filename: str, version: str):
    return f"https://github.com/steveberardi/bigsky/releases/download/v{version}/{filename}"


def download(
    filename: str = BIG_SKY_FILENAME,
    version: str = BIG_SKY_VERSION,
    download_path: str = None,
    digits: int = 4,
):
    download_path = download_path or str(DATA_PATH / filename)
    utils.download(
        url(filename, version),
        download_path,
        "Big Sky Star Catalog",
    )
    to_parquet(
        download_path,
        DataFiles.BIG_SKY,
        digits,
    )


def to_parquet(source_path: str, destination_path: str, digits: int = DIGITS):
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

    df["ra_hours"] = df.apply(
        lambda row: round(row.ra_degrees_j2000 / 15, digits), axis=1
    )

    df = df.assign(epoch_year=2000)

    df = df.rename(
        columns={
            "hip_id": "hip",
            "ra_degrees_j2000": "ra_degrees",
            "dec_degrees_j2000": "dec_degrees",
        }
    )

    df.to_parquet(destination_path, compression="gzip")

    print(f"Done! {destination_path.value}")


def load(path):
    if not exists(path):
        download(filename=BIG_SKY_ASSETS.get(path))

    df = pd.read_parquet(path)

    return df.set_index("tyc_id")


def exists(path) -> bool:
    return os.path.isfile(path)
