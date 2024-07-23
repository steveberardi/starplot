import sys
import os
import requests

from starplot.data import DATA_PATH, DataFiles


BIG_SKY_VERSION = "0.1.0"

BIG_SKY_URL = f"https://github.com/steveberardi/bigsky/releases/download/v{BIG_SKY_VERSION}/bigsky.stars.csv.gz"

DOWNLOADED_PATH = DATA_PATH / "bigsky.stars.csv.gz"

DIGITS = 4


def download():
    with open(DOWNLOADED_PATH, "wb") as f:
        print("Downloading Big Sky Catalog...")

        response = requests.get(BIG_SKY_URL, stream=True)
        total_size = response.headers.get("content-length")

        if total_size is None:
            f.write(response.content)
            return
    
        bytes_written = 0
        total_size = int(total_size)
        for chunk in response.iter_content(chunk_size=4096):
            bytes_written += len(chunk)
            f.write(chunk)
            progress = int(25 * bytes_written / total_size)
            sys.stdout.write("\r[%s%s]" % ("=" * progress, " " * (25 - progress)))
            sys.stdout.flush()
        
        print("Download complete!")


def to_parquet():
    import pandas as pd

    print("Preparing Big Sky Catalog for Starplot...")

    df = pd.read_csv(
        DOWNLOADED_PATH,
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
        lambda row: round(row.ra_degrees_j2000 / 15, DIGITS), axis=1
    )

    df = df.assign(epoch_year=2000)

    df = df.rename(
        columns={
            "hip_id": "hip",
            "ra_degrees_j2000": "ra_degrees",
            "dec_degrees_j2000": "dec_degrees",
        }
    )

    df.to_parquet(DataFiles.BIG_SKY, compression="gzip")


def exists() -> bool:
    return os.path.isfile(DataFiles.BIG_SKY)
