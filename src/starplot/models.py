from typing import Optional
from abc import ABC, abstractmethod

import numpy as np

from starplot.mixins import CreateMapMixin, CreateOpticMixin
from starplot.data.dsos import DsoType
from starplot.data.stars import StarCatalog, STAR_NAMES, load as _load_stars


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
    managers = {}

    def __new__(cls, name, bases, attrs):
        new_cls = super().__new__(cls, name, bases, attrs)

        if "_manager" in attrs:
            Meta.managers[new_cls] = attrs["_manager"]
        
        return new_cls
        
    def __getattribute__(cls, attr):
        if attr == "get":
            return Meta.managers[cls].get

        if attr == "find":
            return Meta.managers[cls].find
    
        if attr == "all":
            return Meta.managers[cls].all

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


class SkyObjectManager(ABC):
    @abstractmethod
    def all(cls, *args, **kwargs):
        raise NotImplementedError

    @classmethod
    def find(cls, where):
        return [s for s in cls.all() if all([e.evaluate(s) for e in where])]

    @classmethod
    def get(cls, **kwargs):
        matches = [
            s
            for s in cls.all()
            if all([getattr(s, kw) == value for kw, value in kwargs.items()])
        ]

        if len(matches) == 1:
            return matches[0]
        elif len(matches) > 1:
            raise ValueError("More than one match. Use find() instead or narrow your search.")
        else:
            return None

class StarManager(SkyObjectManager):
    @classmethod
    def all(cls, catalog: StarCatalog = StarCatalog.HIPPARCOS):
        all_stars = _load_stars(catalog)

        # TODO : add datetime kwarg

        for s in all_stars.itertuples():
            hip_id = s.Index
            obj = Star(ra=s.ra_hours, dec=s.dec_degrees, magnitude=s.magnitude, bv=s.bv)

            if np.isfinite(hip_id):
                obj.hip = hip_id
                obj.name = STAR_NAMES.get(hip_id)

            yield obj

class Star(SkyObject, CreateMapMixin, CreateOpticMixin):
    """
    Star model. An instance of this model is passed to any [callables](/reference-callables) you define when plotting stars.
    So, you can use any attributes of this model in your callables. Note that some may be null.
    """

    _manager = StarManager

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


class DsoManager(SkyObjectManager):
    @classmethod
    def all(cls):
        from starplot.data.dsos import load_ongc, ONGC_TYPE_MAP

        all_dsos = load_ongc()

        for d in all_dsos.itertuples():
            magnitude = d.mag_v or d.mag_b or None
            magnitude = float(magnitude) if magnitude else None
            yield DSO(
                name=d.name,
                ra=d.ra_degrees / 15,
                dec=d.dec_degrees,
                type=ONGC_TYPE_MAP[d.type],
                maj_ax=d.maj_ax,
                min_ax=d.min_ax,
                angle=d.angle,
                magnitude=magnitude,
                size=d.size_deg2,
                m=d.m,
            )

class DSO(SkyObject, CreateMapMixin, CreateOpticMixin):
    """
    Deep Sky Object (DSO) model. An instance of this model is passed to any [callables](/reference-callables) you define when plotting DSOs.
    So, you can use any attributes of this model in your callables. Note that some may be null.
    """

    _manager = DsoManager

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

    m: Optional[int] = None
    """Messier number, (if available)"""

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
        m: int = None,
    ) -> None:
        super().__init__(ra, dec)
        self.name = name
        self.type = type
        self.magnitude = magnitude
        self.maj_ax = maj_ax
        self.min_ax = min_ax
        self.angle = angle
        self.size = size

        if m is not None:
            self.m = int(m)

    def __repr__(self) -> str:
        return f"DSO(name={self.name}, magnitude={self.magnitude})"

    @classmethod
    def get(where: list):
        """Get a DSO"""
        pass

    @classmethod
    def find(where: list) -> list["DSO"]:
        """
        Find DSOs

        Args:
            where: A list of expressions that determine which DSOs to find. See [Selecting Objects](/reference-selecting-objects/) for details.

        Returns:
            List of DSOs that match all `where` expressions

        """
        pass




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
