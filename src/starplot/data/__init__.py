from skyfield.api import Loader

from starplot.config import settings, DATA_PATH
from .catalogs import Catalog  # noqa: F401

load = Loader(settings.data_path)  # used for loading ephemeris


class DataFiles:
    BIG_SKY = settings.data_path / "bigsky.0.4.0.stars.parquet"

    BIG_SKY_MAG9 = DATA_PATH / "bigsky.0.4.0.stars.mag9.parquet"

    CONSTELLATIONS = DATA_PATH / "constellations.parquet"

    ONGC = DATA_PATH / "ongc.parquet"

    DATABASE = DATA_PATH / "sky.db"
