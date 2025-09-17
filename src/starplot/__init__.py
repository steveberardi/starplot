"""Star charts and maps of the sky"""

__version__ = "0.16.3"

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
    Planet,  # noqa: F401
    Moon,  # noqa: F401
    Sun,  # noqa: F401
    ObjectList,  # noqa: F401
)
from .styles import *  # noqa: F401 F403
from .observer import Observer  # noqa: F401
from .projections import *  # noqa: F401 F403
from .config import settings  # noqa: F401

from ibis import _  # noqa: F401 F403
