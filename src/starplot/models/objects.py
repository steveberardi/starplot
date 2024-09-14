from starplot.models import Star, DSO, Moon, Sun, Planet, Constellation


class ObjectList(object):
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
