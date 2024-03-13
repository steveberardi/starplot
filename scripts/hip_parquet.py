"""Creates a parquet file of the Hipparcos star catalog"""

from pandas import read_csv
from skyfield.api import load
from skyfield.data import hipparcos


def load_dataframe(fobj, extra_columns=None):
    """
    Given an open file for ``hip_main.dat``, return a parsed dataframe.

    If the file is gzipped, it will be automatically uncompressed.

    Adapted from: https://github.com/skyfielders/python-skyfield/blob/master/skyfield/data/hipparcos.py

    Args:
        extra_columns: list of extra columns to read

    """
    extra_columns = extra_columns or []
    fobj.seek(0)
    magic = fobj.read(2)
    compression = "gzip" if (magic == b"\x1f\x8b") else None
    fobj.seek(0)

    df = read_csv(
        fobj,
        sep="|",
        names=hipparcos._COLUMN_NAMES,
        compression=compression,
        usecols=["HIP", "Vmag", "RAdeg", "DEdeg", "Plx", "pmRA", "pmDE"]
        + extra_columns,
        na_values=["     ", "       ", "        ", "            "],
        skipinitialspace=True,
    )
    df.columns = (
        "hip",
        "magnitude",
        "ra_degrees",
        "dec_degrees",
        "parallax_mas",
        "ra_mas_per_year",
        "dec_mas_per_year",
        *[c.replace("-", "").lower() for c in extra_columns],
    )
    df = df.assign(
        ra_hours=df["ra_degrees"] / 15.0,
        epoch_year=1991.25,
    )
    return df.set_index("hip")


# load hipparcos stars via Skyfield API
with load.open(hipparcos.URL) as f:
    hipstars = load_dataframe(f, extra_columns=["B-V"])

# convert to parquet
hipstars.to_parquet("temp/stars.hipparcos.parquet", index=True, compression="gzip")

# also save to CSV for QA
hipstars.to_csv("temp/stars.hipparcos.csv")
