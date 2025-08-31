from skyfield.api import Loader

from starplot.config import settings, DATA_PATH

load = Loader(DATA_PATH)


class DataFiles:
    BIG_SKY = settings.download_path / "bigsky.0.4.0.stars.parquet"

    BIG_SKY_MAG11 = DATA_PATH / "bigsky.0.4.0.stars.mag11.parquet"

    DATABASE = DATA_PATH / "sky.db"
