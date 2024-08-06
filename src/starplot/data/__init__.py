import os

from enum import Enum
from pathlib import Path

from skyfield.api import Loader

HERE = Path(__file__).resolve().parent
DATA_PATH = HERE / "library"

load = Loader(DATA_PATH)


def env(name, default):
    return os.environ.get(name) or default


class DataFiles(str, Enum):
    # Built-In Files
    CONSTELLATION_LINES = DATA_PATH / "constellation_lines_inv.gpkg"
    CONSTELLATION_LINES_HIP = DATA_PATH / "constellation_lines_hips.json"
    CONSTELLATION_BORDERS = DATA_PATH / "constellation_borders_inv.gpkg"
    MILKY_WAY = DATA_PATH / "milkyway.gpkg"
    HIPPARCOS = DATA_PATH / "stars.hipparcos.parquet"
    BIG_SKY_MAG11 = DATA_PATH / "stars.bigsky.mag11.parquet"
    ONGC = DATA_PATH / "ongc.gpkg.zip"
    CONSTELLATIONS = DATA_PATH / "constellations.gpkg"

    # Downloaded Files
    _DOWNLOAD_PATH = Path(env("STARPLOT_DOWNLOAD_PATH", str(DATA_PATH)))
    BIG_SKY = _DOWNLOAD_PATH / "stars.bigsky.parquet"
