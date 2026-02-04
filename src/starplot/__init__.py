# ruff: noqa: F401,F403

"""Star charts and maps of the sky"""

__version__ = "0.19.5"

from .plots import (
    MapPlot,
    HorizonPlot,
    OpticPlot,
    ZenithPlot,
)
from .models import (
    DSO,
    DsoType,
    Star,
    Constellation,
    ConstellationBorder,
    Comet,
    Planet,
    Moon,
    Sun,
    ObjectList,
    Scope,
    Binoculars,
    Reflector,
    Refractor,
    Camera,
    Satellite,
    Observer,
    MilkyWay,
)
from .data import Catalog
from .styles import *
from .projections import *
from .config import settings
from .plotters.text import CollisionHandler

from ibis import _


import contextlib


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
