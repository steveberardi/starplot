from starplot.models import Star, DSO, Moon, Sun
from starplot.models.base import SkyObject


class Planet(SkyObject):
    """Planet model."""

    name: str
    """Name of the planet"""

    def __init__(self, ra: float, dec: float, name: str) -> None:
        super().__init__(ra, dec)
        self.name = name


class ObjectList(object):
    """Lists of objects that have been plotted"""

    stars: list[Star] = None
    """Stars"""

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
