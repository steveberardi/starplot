# ruff: noqa: F401

"""Star charts and maps of the sky"""

__version__ = "0.22.0"

from ibis import _

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
    NakedEye,
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
from .settings import Settings, settings
from .styles import *
