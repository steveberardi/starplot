from skyfield.api import Loader

from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA_PATH = HERE / "data"

load = Loader(DATA_PATH)
