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

    _constellation_id: Optional[str] = None

    @property
    def constellation_id(self) -> str | None:
        """Identifier of the constellation that contains this object. The ID is the three-letter (all lowercase) abbreviation from the International Astronomical Union (IAU)."""
        if not self._constellation_id:
            pos = position_of_radec(self.ra / 15, self.dec)
            self._constellation_id = constellation_at()(pos).lower()
        return self._constellation_id

    def constellation(self):
        """Returns an instance of the [`Constellation`][starplot.models.Constellation] that contains this object"""
        from starplot.models import Constellation

        return Constellation.get(iau_id=self.constellation_id)

    @classmethod
    @cache
    def _dir(cls):
        return dir(cls)
