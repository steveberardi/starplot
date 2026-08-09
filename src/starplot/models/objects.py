from starplot.models.constellation import Constellation
from starplot.models.dso import DSO
from starplot.models.moon import Moon
from starplot.models.planet import Planet
from starplot.models.star import Star
from starplot.models.sun import Sun


class ObjectList:
    """Lists of objects that have been plotted. An instance of this model is returned by a plot's `objects` property."""

    stars: list[Star] = None
    """Stars"""

    constellations: list[Constellation] = None
    """Constellations"""

    dsos: list[DSO] = None
    """Deep Sky Objects (DSOs)"""

    planets: list[Planet] = None
    """Planets"""

    moon: Moon = None
    """Moon"""

    sun: Sun = None
    """Sun"""

    def __init__(self, *args, **kwargs) -> None:
        self.stars = []
        self.dsos = []
        self.planets = []
        self.constellations = []
