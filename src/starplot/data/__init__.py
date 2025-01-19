from skyfield.api import Loader

from starplot import settings

load = Loader(settings.DATA_PATH)


class DataFiles:
    BIG_SKY = settings.DOWNLOAD_PATH / "bigsky.0.4.0.stars.parquet"

    BIG_SKY_MAG11 = settings.DATA_PATH / "bigsky.0.4.0.stars.mag11.parquet"

    DATABASE = settings.DATA_PATH / "sky.db"
