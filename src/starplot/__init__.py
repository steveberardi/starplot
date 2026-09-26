# ruff: noqa: F401

"""Star charts and maps of the sky"""

__version__ = "0.21.0"

import contextlib

from ibis import _

from .config import settings
from .data import Catalog
from .models import (
    DSO,
    Binoculars,
    Camera,
    Comet,
    Constellation,
    ConstellationBorder,
    DsoType,
    MilkyWay,
    Moon,
    ObjectList,
    Observer,
    Planet,
    Reflector,
    Refractor,
    Satellite,
    Scope,
    Star,
    Sun,
)
from .plots import (
    GalaxyPlot,
    HorizonPlot,
    MapPlot,
    OpticPlot,
    ZenithPlot,
)
from .plotters.text import CollisionHandler
from .projections import *
from .styles import *


@contextlib.contextmanager
def override_settings(**kwargs):
    original = {}

    for key, value in kwargs.items():
        original[key] = getattr(settings, key, None)
        setattr(settings, key, value)

    try:
        yield

    finally:
        for key, value in original.items():
            setattr(settings, key, value)
