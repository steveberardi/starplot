from enum import Enum
from pathlib import Path

from skyfield.api import Loader

HERE = Path(__file__).resolve().parent
DATA_PATH = HERE / "library"

load = Loader(DATA_PATH)


class DataFiles(str, Enum):
    CONSTELLATION_LINES = DATA_PATH / "i.constellations.lines.json"
    CONSTELLATION_BORDERS = DATA_PATH / "i.constellations.borders.json"
    MILKY_WAY = DATA_PATH / "i.milkyway.split.json"
    TYCHO_1 = DATA_PATH / "stars.tycho-1.csv.gz"
