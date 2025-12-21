"""Star charts and maps of the sky"""

__version__ = "0.18.0b2"

from .base import BasePlot  # noqa: F401
from .map import MapPlot  # noqa: F401
from .horizon import HorizonPlot  # noqa: F401
from .optic import OpticPlot  # noqa: F401
from .zenith import ZenithPlot  # noqa: F401
from .models import (
    DSO,  # noqa: F401
    DsoType,  # noqa: F401
    Star,  # noqa: F401
    Constellation,  # noqa: F401
    Comet,  # noqa: F401
    Planet,  # noqa: F401
    Moon,  # noqa: F401
    Sun,  # noqa: F401
    ObjectList,  # noqa: F401
    Scope,  # noqa: F401
    Binoculars,  # noqa: F401
    Reflector,  # noqa: F401
    Refractor,  # noqa: F401
    Camera,  # noqa: F401
    Satellite,  # noqa: F401
    Observer,  # noqa: F401
)
from .styles import *  # noqa: F401 F403
from .projections import *  # noqa: F401 F403
from .config import settings  # noqa: F401

from ibis import _  # noqa: F401 F403


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
