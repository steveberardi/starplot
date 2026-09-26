# ruff: noqa: F401

from pathlib import Path

from skyfield.api import Loader

from starplot.config import settings

load = Loader(settings.data_path)  # used for loading ephemeris

# Must come after `load` is defined: catalogs.py pulls in starplot.models, whose
# package __init__ imports comet.py, which needs `starplot.data.load` to already
# exist. isort would otherwise hoist this back above `load` and reintroduce that
# circular import.
from .catalogs import Catalog  # noqa: I001


HERE = Path(__file__).resolve().parent

INTERNAL_DATA_PATH = HERE / "library"
"""Path of starplot data"""


class DataFiles:
    STAR_DESIGNATIONS = INTERNAL_DATA_PATH / "star_designations.parquet"
    CONSTELLATION_NAMES = INTERNAL_DATA_PATH / "constellation_names.parquet"
    DSO_NAMES = INTERNAL_DATA_PATH / "dso_names.parquet"
