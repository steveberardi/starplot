from dataclasses import dataclass, fields
from functools import cache
from typing import Optional

import pyarrow as pa
from skyfield.api import position_of_radec, load_constellation_map

from starplot.mixins import CreateMapMixin, CreateOpticMixin


@cache
def constellation_at():
    return load_constellation_map()


@dataclass(slots=True, kw_only=True)
class SkyObject(
    CreateMapMixin,
    CreateOpticMixin,
):
    """
    Base class for sky objects.

    All sky object classes inherit from this base class.
    """

    ra: float
    """Right Ascension, in degrees (0 to 360)"""

    dec: float
    """Declination, in degrees (-90 to 90)"""

    constellation_id: Optional[str] = None
    """Three-letter IAU id of the constellation that contains this object"""

    healpix_index: int = None
    """[HEALPix](https://en.wikipedia.org/wiki/HEALPix) pixel index of this object's RA/DEC"""

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

    @classmethod
    @cache
    def _fields(cls):
        return [f.name for f in fields(cls)]

    @classmethod
    @cache
    def _pyarrow_schema(cls):
        """Returns explicit schema"""
        return pa.schema(
            [
                pa.field("ra", pa.float64(), nullable=False),
                pa.field("dec", pa.float64(), nullable=False),
                pa.field("constellation_id", pa.string()),
                pa.field("healpix_index", pa.int64()),
            ]
        )


@dataclass(kw_only=True)
class CatalogObject:
    pk: int
    """Primary key of object in catalog. Needs to be unique across all objects in the catalog."""
