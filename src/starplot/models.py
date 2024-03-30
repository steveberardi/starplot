from typing import Optional

from starplot.data.dsos import DsoType


class Expression:
    def __init__(self, func=None) -> None:
        self.func = func

    def evaluate(self, obj):
        return self.func(obj)

    def __or__(self, other):
        return Expression(func=lambda d: self.evaluate(d) or other.evaluate(d))

    def __and__(self, other):
        return Expression(func=lambda d: self.evaluate(d) and other.evaluate(d))


class Term:
    def _factory(self, func):
        def exp(c):
            value = getattr(c, self.attr)

            if value is None:
                return False

            return func(value)

        return Expression(func=exp)

    def __init__(self, attr):
        self.attr = attr

    def __eq__(self, other):
        return Expression(
            func=lambda c: getattr(c, self.attr) == other
            if other is not None
            else getattr(c, self.attr) is None
        )

    def __ne__(self, other):
        return Expression(
            func=lambda c: getattr(c, self.attr) != other
            if other is not None
            else getattr(c, self.attr) is not None
        )

    def __lt__(self, other):
        return self._factory(lambda value: value < other)

    def __le__(self, other):
        return self._factory(lambda value: value <= other)

    def __gt__(self, other):
        return self._factory(lambda value: value > other)

    def __ge__(self, other):
        return self._factory(lambda value: value >= other)

    def is_in(self, other):
        """Returns `True` if `other` is in the field value"""
        return Expression(func=lambda c: getattr(c, self.attr) in other)

    def is_not_in(self, other):
        """Returns `True` if `other` is NOT in the field value"""
        return Expression(func=lambda c: getattr(c, self.attr) not in other)

    def is_null(self):
        """Returns `True` if the field value is `None`"""
        return Expression(func=lambda c: getattr(c, self.attr) is None)

    def is_not_null(self):
        """Returns `True` if the field value is NOT `None`"""
        return Expression(func=lambda c: getattr(c, self.attr) is not None)


class Meta(type):
    def __getattribute__(cls, attr):
        return Term(attr)


class SkyObject(metaclass=Meta):
    """
    Basic sky object model.
    """

    ra: float
    """Right Ascension, in hours (0...24)"""

    dec: float
    """Declination, in degrees (-90...90)"""

    def __init__(self, ra: float, dec: float) -> None:
        self.ra = ra
        self.dec = dec


class Star(SkyObject):
    """
    Star model. An instance of this model is passed to any [callables](/reference-callables) you define when plotting stars.
    So, you can use any attributes of this model in your callables. Note that some may be null.
    """

    magnitude: float
    """Magnitude"""

    bv: Optional[float] = None
    """B-V Color Index, if available"""

    hip: Optional[int] = None
    """Hipparcos Catalog ID, if available"""

    name: Optional[str] = None
    """Name, if available"""

    def __init__(
        self,
        ra: float,
        dec: float,
        magnitude: float,
        bv: float = None,
        hip: int = None,
        name: str = None,
    ) -> None:
        super().__init__(ra, dec)
        self.magnitude = magnitude
        self.bv = bv
        self.hip = hip
        self.name = name


class DSO(SkyObject):
    """
    Deep Sky Object (DSO) model. An instance of this model is passed to any [callables](/reference-callables) you define when plotting DSOs.
    So, you can use any attributes of this model in your callables. Note that some may be null.
    """

    name: str
    """Name of the DSO (as specified in OpenNGC)"""

    type: DsoType

    magnitude: Optional[float] = None
    """Magnitude (if available)"""

    maj_ax: Optional[float] = None
    """Major axis of the DSO, in arcmin (if available)"""

    min_ax: Optional[float] = None
    """Minor axis of the DSO, in arcmin (if available)"""

    angle: Optional[float] = None
    """Angle of the DSO, in degrees (if available)"""

    size: Optional[float] = None
    """Size of the DSO calculated as the area of the minimum bounding rectangle of the DSO, in degrees squared (if available)"""

    def __init__(
        self,
        ra: float,
        dec: float,
        name: str,
        type: DsoType,
        magnitude: float = None,
        maj_ax: float = None,
        min_ax: float = None,
        angle: float = None,
        size: float = None,
    ) -> None:
        super().__init__(ra, dec)
        self.name = name
        self.type = type
        self.magnitude = magnitude
        self.maj_ax = maj_ax
        self.min_ax = min_ax
        self.angle = angle
        self.size = size


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
