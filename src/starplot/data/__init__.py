import os

from pathlib import Path

from skyfield.api import Loader

HERE = Path(__file__).resolve().parent
DATA_PATH = HERE / "library"


def env(name, default):
    return os.environ.get(name) or default


DOWNLOAD_PATH = Path(env("STARPLOT_DOWNLOAD_PATH", str(DATA_PATH)))
DUCKDB_EXTENSION_PATH = Path(
    env("STARPLOT_DUCKDB_EXTENSIONS_PATH", str(DATA_PATH / "duckdb-extensions"))
)


load = Loader(DATA_PATH)


class DataFiles:
    # Built-In Files
    CONSTELLATION_LINES = DATA_PATH / "constellation_lines_inv.gpkg"
    CONSTELLATION_LINES_HIP = DATA_PATH / "constellation_lines_hips.json"
    CONSTELLATION_BORDERS = DATA_PATH / "constellation_borders_inv.gpkg"
    MILKY_WAY = DATA_PATH / "milkyway.gpkg"

    # BIG_SKY_MAG11 = DATA_PATH / "stars.bigsky.mag11.parquet"
    BIG_SKY_MAG11 = DATA_PATH / "stars.bigsky.0.4.0.mag10.parquet"

    ONGC = DATA_PATH / "ongc.gpkg.zip"
    CONSTELLATIONS = DATA_PATH / "constellations.gpkg"

    BIG_SKY = DOWNLOAD_PATH / "stars.bigsky.parquet"

    DATABASE = DATA_PATH / "sky.db"
