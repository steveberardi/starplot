from enum import Enum
from pathlib import Path

from skyfield.api import Loader

HERE = Path(__file__).resolve().parent
DATA_PATH = HERE / "library"

load = Loader(DATA_PATH)


class DataFiles(str, Enum):
    CONSTELLATION_LINES = DATA_PATH / "constellation_lines_inv.gpkg"
    CONSTELLATION_LINES_HIP = DATA_PATH / "constellation_lines_hips.json"
    CONSTELLATION_BORDERS = DATA_PATH / "constellation_borders_inv.gpkg"
    MILKY_WAY = DATA_PATH / "milkyway.gpkg"
    HIPPARCOS = DATA_PATH / "stars.hipparcos.parquet"
    TYCHO_1 = DATA_PATH / "stars.tycho-1.gz.parquet"
    ONGC = DATA_PATH / "ongc.gpkg.zip"
    CONSTELLATIONS = DATA_PATH / "constellations.gpkg"
