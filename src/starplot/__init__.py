"""Star charts and maps of the sky"""

__version__ = "0.15.8"

from .base import BasePlot  # noqa: F401
from .map import MapPlot, Projection  # noqa: F401
from .horizon import HorizonPlot  # noqa: F401
from .optic import OpticPlot  # noqa: F401
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
from ibis import _  # noqa: F401 F403
