from skyfield.api import Loader

from starplot.config import settings

load = Loader(settings.data_path)


class DataFiles:
    BIG_SKY = settings.download_path / "bigsky.0.4.0.stars.parquet"

    BIG_SKY_MAG11 = settings.data_path / "bigsky.0.4.0.stars.mag11.parquet"

    DATABASE = settings.data_path / "sky.db"
