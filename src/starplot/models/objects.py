from starplot.models import Star, DSO
from starplot.models.base import SkyObject


class Planet(SkyObject):
    """Planet model."""

    name: str
    """Name of the planet"""

    def __init__(self, ra: float, dec: float, name: str) -> None:
        super().__init__(ra, dec)
        self.name = name


class Moon(SkyObject):
    """Moon model. Only used for Earth's moon right now, but will potentially represent other planets' moons in future versions."""

    name: str = "Moon"
    """Name of the moon"""

    def __init__(self, ra: float, dec: float, name: str) -> None:
        super().__init__(ra, dec)
        self.name = name


class Sun(SkyObject):
    """Sun model."""

    name: str = "Sun"
    """Name of the Sun"""

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