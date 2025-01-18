from typing import Union, Iterator

from ibis import _
from shapely import Polygon, MultiPolygon

from starplot.models.base import SkyObject
from starplot.data import constellations


class Constellation(SkyObject):
    """
    Constellation model.
    """

    iau_id: str = None
    """
    International Astronomical Union (IAU) three-letter designation, all lowercase.
    
    **Important**: Starplot treats Serpens as two separate constellations to make them easier to work with programatically. 
    Serpens Caput has the `iau_id` of `ser1` and Serpens Cauda is `ser2`
    """

    name: str = None
    """Name"""

    star_hip_ids: list[int] = None
    """List of HIP ids for stars that are part of the _lines_ for this constellation."""

    boundary: Union[Polygon, MultiPolygon] = None
    """Shapely Polygon of the constellation's boundary. Right ascension coordinates are in degrees (0...360)."""

    def __init__(
        self,
        ra: float,
        dec: float,
        iau_id: str,
        name: str = None,
        star_hip_ids: list[int] = None,
        boundary: Polygon = None,
    ) -> None:
        super().__init__(ra, dec, constellation_id=iau_id.lower())
        self.iau_id = iau_id.lower()
        self.name = name
        self.star_hip_ids = star_hip_ids
        self.boundary = boundary

    def __repr__(self) -> str:
        return f"Constellation(iau_id={self.iau_id}, name={self.name}, ra={self.ra}, dec={self.dec})"

    @classmethod
    def all(cls) -> Iterator["Constellation"]:
        df = constellations.load().to_pandas()

        for c in df.itertuples():
            yield from_tuple(c)

    @classmethod
    def get(cls, **kwargs) -> "Constellation":
        """
        Get a Constellation, by matching its attributes.

        Example:

            hercules = Constellation.get(name="Hercules")

        Args:
            **kwargs: Attributes on the constellation you want to match

        Raises: `ValueError` if more than one constellation is matched
        """
        filters = []

        for k, v in kwargs.items():
            filters.append(getattr(_, k) == v)

        df = constellations.load(filters=filters).to_pandas()
        results = [from_tuple(c) for c in df.itertuples()]

        if len(results) == 1:
            return results[0]

        if len(results) > 1:
            raise ValueError(
                "More than one match. Use find() instead or narrow your search."
            )

        return None

    @classmethod
    def find(cls, where: list) -> list["Constellation"]:
        """
        Find Constellations

        Args:
            where: A list of expressions that determine which constellations to find. See [Selecting Objects](/reference-selecting-objects/) for details.

        Returns:
            List of Constellations that match all `where` expressions

        """
        df = constellations.load(filters=where).to_pandas()

        return [from_tuple(c) for c in df.itertuples()]

    def constellation(self):
        """Not applicable to Constellation model, raises `NotImplementedError`"""
        raise NotImplementedError()


def from_tuple(c: tuple) -> Constellation:
    return Constellation(
        ra=c.ra,
        dec=c.dec,
        iau_id=c.iau_id,
        name=c.name,
        star_hip_ids=c.star_hip_ids,
        boundary=c.geometry,
    )
