import os
from pathlib import Path


from starplot.config import settings
from starplot.data import DataFiles, utils, Catalog


BIG_SKY_VERSION = "0.4.0"
BIG_SKY_FILENAME = f"bigsky.{BIG_SKY_VERSION}.stars.csv.gz"
BIG_SKY_PQ_FILENAME = f"bigsky.{BIG_SKY_VERSION}.stars.parquet"

BIG_SKY_MAG9_FILENAME = f"bigsky.{BIG_SKY_VERSION}.stars.mag9.csv.gz"
BIG_SKY_MAG9_PQ_FILENAME = f"bigsky.{BIG_SKY_VERSION}.stars.mag9.parquet"


def get_url(version: str = BIG_SKY_VERSION, filename: str = BIG_SKY_FILENAME):
    return f"https://github.com/steveberardi/bigsky/releases/download/v{version}/{filename}"


def download(
    url: str = None,
    download_path: str = settings.data_path,
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
    build(
        source_path=full_download_path,
        destination_path=build_file,
        limiting_magnitude=20,
    )


def build(source_path: str, destination_path: str, limiting_magnitude: float = 16):
    import pandas as pd

    from shapely import Point

    from starplot.models import Star

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
            "tyc_id": "tyc",
            "ra_degrees_j2000": "ra",
            "dec_degrees_j2000": "dec",
            "constellation": "constellation_id",
        }
    )

    def stars(d):
        for star in d.itertuples():
            geometry = Point(star.ra, star.dec)

            if (
                not geometry.is_valid
                or geometry.is_empty
                or star.magnitude > limiting_magnitude
            ):
                continue

            yield Star(
                hip=star.hip,
                tyc=star.tyc,
                ra=star.ra,
                dec=star.dec,
                constellation_id=star.constellation_id,
                ccdm=star.ccdm,
                magnitude=star.magnitude,
                parallax_mas=star.parallax_mas,
                ra_mas_per_year=star.ra_mas_per_year or 0,
                dec_mas_per_year=star.dec_mas_per_year or 0,
                bv=star.bv,
                geometry=geometry,
                epoch_year=2000,
            )

    Catalog.build(
        objects=stars(df),
        path=destination_path,
        chunk_size=5_000_000,
        columns=[
            "hip",
            "tyc",
            "ra",
            "dec",
            "magnitude",
            "bv",
            "parallax_mas",
            "ra_mas_per_year",
            "dec_mas_per_year",
            "constellation_id",
            "geometry",
            "ccdm",
            "epoch_year",
        ],
        partition_columns=[],
        sorting_columns=["magnitude"],
        compression="snappy",
        row_group_size=100_000,
    )

    print(f"Done! {destination_path}")


def exists(path) -> bool:
    return os.path.isfile(path)


def download_if_not_exists(
    filename: str = DataFiles.BIG_SKY,
    url: str = None,
    download_path: str = settings.download_path,
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
