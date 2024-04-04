from abc import ABC, abstractmethod

from starplot.models.meta import Meta


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
            raise ValueError(
                "More than one match. Use find() instead or narrow your search."
            )
        else:
            return None
