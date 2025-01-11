from skyfield.api import Loader

from starplot import settings

load = Loader(settings.DATA_PATH)


class DataFiles:

    BIG_SKY_MAG11 = settings.DATA_PATH / "stars.bigsky.0.4.0.mag10.parquet"

    BIG_SKY = settings.DOWNLOAD_PATH / "stars.bigsky.parquet"

    DATABASE = settings.DATA_PATH / "sky.db"


class RawDataFiles:
    MILKY_WAY = settings.DATA_PATH / "source" / "milkyway.json"
    CONSTELLATION_BORDERS = settings.DATA_PATH / "source" / "constellation_borders.json"
