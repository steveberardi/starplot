from typing import Optional
from abc import ABC, abstractmethod

from skyfield.api import position_of_radec, load_constellation_map

from starplot.mixins import CreateMapMixin, CreateOpticMixin

constellation_at = load_constellation_map()


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
        """Returns `True` if the field's value is in `other`"""
        return Expression(func=lambda c: getattr(c, self.attr) in other)

    def is_not_in(self, other):
        """Returns `True` if the field's value is NOT in `other`"""
        return Expression(func=lambda c: getattr(c, self.attr) not in other)

    def is_null(self):
        """Returns `True` if the field value is `None`"""
        return Expression(func=lambda c: getattr(c, self.attr) is None)

    def is_not_null(self):
        """Returns `True` if the field value is NOT `None`"""
        return Expression(func=lambda c: getattr(c, self.attr) is not None)

    def intersects(self, other):
        """Returns `True` if the field's value intersects `other`. Only available for geometry-type fields."""
        return Expression(func=lambda c: getattr(c, self.attr).intersects(other))


class Meta(type):
    managers = {}

    def __new__(cls, name, bases, attrs):
        new_cls = super().__new__(cls, name, bases, attrs)

        if "_manager" in attrs:
            Meta.managers[new_cls] = attrs["_manager"]

        return new_cls

    def __getattribute__(cls, attr):
        if attr in ["get", "find", "all"]:
            return getattr(Meta.managers[cls], attr)

        return Term(attr)


class SkyObject(CreateMapMixin, CreateOpticMixin, metaclass=Meta):
    """
    Basic sky object model.
    """

    ra: float
    """Right Ascension, in hours (0...24)"""

    dec: float
    """Declination, in degrees (-90...90)"""

    constellation_id: Optional[str] = None
    """Identifier of the constellation that contains this object. The ID is the three-letter (all lowercase) abbreviation from the International Astronomical Union (IAU)."""

    def __init__(self, ra: float, dec: float) -> None:
        self.ra = ra
        self.dec = dec

        pos = position_of_radec(ra, dec)
        self.constellation_id = constellation_at(pos).lower()

    def constellation(self):
        """Returns an instance of the [`Constellation`][starplot.models.Constellation] that contains this object"""
        from starplot.models import Constellation

        return Constellation.get(iau_id=self.constellation_id)


class SkyObjectManager(ABC):
    @abstractmethod
    def all(cls, *args, **kwargs):
        raise NotImplementedError

    @classmethod
    def find(cls, where, **kwargs):
        all_objects = kwargs.pop("all_objects", None) or cls.all()
        return [s for s in all_objects if all([e.evaluate(s) for e in where])]

    @classmethod
    def get(cls, **kwargs):
        all_objects = kwargs.pop("all_objects", None) or cls.all()
        matches = [
            s
            for s in all_objects
            if all([getattr(s, kw) == value for kw, value in kwargs.items()])
        ]

        if len(matches) == 1:
            return matches[0]
        elif len(matches) > 1:
            raise ValueError(
                "More than one match. Use find() instead or narrow your search."
            )
        else:
            return None
