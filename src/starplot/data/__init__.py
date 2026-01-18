# ruff: noqa: F401,F403

from pathlib import Path

from skyfield.api import Loader

from starplot.config import settings
from .catalogs import Catalog

load = Loader(settings.data_path)  # used for loading ephemeris


HERE = Path(__file__).resolve().parent

INTERNAL_DATA_PATH = HERE / "library"
"""Path of starplot data"""


class DataFiles:
    STAR_DESIGNATIONS = INTERNAL_DATA_PATH / "star_designations.parquet"
    CONSTELLATION_NAMES = INTERNAL_DATA_PATH / "constellation_names.parquet"
    DSO_NAMES = INTERNAL_DATA_PATH / "dso_names.parquet"
