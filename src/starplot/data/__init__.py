from skyfield.api import Loader

from starplot import settings

load = Loader(settings.DATA_PATH)


class DataFiles:
    CONSTELLATIONS = settings.DATA_PATH / "constellations.gpkg"

    CONSTELLATION_LINES_HIP = settings.DATA_PATH / "constellation_lines_hips.json"

    BIG_SKY_MAG11 = settings.DATA_PATH / "stars.bigsky.0.4.0.mag10.parquet"

    BIG_SKY = settings.DOWNLOAD_PATH / "stars.bigsky.parquet"

    DATABASE = settings.DATA_PATH / "sky.db"
