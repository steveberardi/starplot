from functools import cache
from typing import Optional

from skyfield.api import position_of_radec, load_constellation_map

from starplot.mixins import CreateMapMixin, CreateOpticMixin


@cache
def constellation_at():
    return load_constellation_map()


class SkyObject(CreateMapMixin, CreateOpticMixin):
    """
    Basic sky object model.
    """

    ra: float
    """Right Ascension, in degrees (0...360)"""

    dec: float
    """Declination, in degrees (-90...90)"""

    _constellation_id = None

    constellation_id: Optional[str] = None
    """Identifier of the constellation that contains this object. The ID is the three-letter (all lowercase) abbreviation from the International Astronomical Union (IAU)."""

    def __init__(self, ra: float, dec: float, constellation_id: str = None) -> None:
        self.ra = ra
        self.dec = dec
        if constellation_id:
            self._constellation_id = constellation_id

    @property
    def constellation_id(self):
        """Identifier of the constellation that contains this object. The ID is the three-letter (all lowercase) abbreviation from the International Astronomical Union (IAU)."""
        if not self._constellation_id:
            pos = position_of_radec(self.ra, self.dec)
            self._constellation_id = constellation_at()(pos).lower()
        return self._constellation_id

    def constellation(self):
        """Returns an instance of the [`Constellation`][starplot.models.Constellation] that contains this object"""
        from starplot.models import Constellation

        return Constellation.get(iau_id=self.constellation_id)
