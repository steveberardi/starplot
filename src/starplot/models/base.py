from dataclasses import dataclass
from functools import cache
from typing import Optional

from skyfield.api import position_of_radec, load_constellation_map

from starplot.mixins import CreateMapMixin, CreateOpticMixin


@cache
def constellation_at():
    return load_constellation_map()


@dataclass(slots=True)
class SkyObject(
    CreateMapMixin,
    CreateOpticMixin,
):
    """
    Basic sky object model.
    """

    ra: float
    """Right Ascension, in degrees (0 to 360)"""

    dec: float
    """Declination, in degrees (-90 to 90)"""

    constellation_id: Optional[str] = None
    """Three-letter IAU id of the constellation that contains this object"""

    def constellation(self):
        """Returns an instance of the [`Constellation`][starplot.models.Constellation] that contains this object, or `None` if no constellation is found."""
        from starplot.models import Constellation

        return Constellation.get(iau_id=self.constellation_id)

    def populate_constellation_id(self):
        """Populates the constellation_id field based on the location of this object"""
        pos = position_of_radec(self.ra / 15, self.dec)
        self.constellation_id = constellation_at()(pos).lower()

    @classmethod
    @cache
    def _dir(cls):
        return dir(cls)
