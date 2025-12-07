from skyfield.api import Loader

from starplot.config import settings, DATA_PATH
from .catalog import Catalog  # noqa: F401

load = Loader(DATA_PATH)


class DataFiles:
    BIG_SKY = settings.download_path / "bigsky.0.4.0.stars.parquet"

    BIG_SKY_MAG9 = DATA_PATH / "bigsky.0.4.0.stars.mag9.parquet"

    DATABASE = DATA_PATH / "sky.db"
