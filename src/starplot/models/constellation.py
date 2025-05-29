from typing import Iterator

from ibis import _

from starplot.models.base import SkyObject, ShapelyPolygon, ShapelyMultiPolygon
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
    """Name of constellation"""

    star_hip_ids: list[int] = None
    """List of HIP ids for stars that are part of the _lines_ for this constellation."""

    boundary: ShapelyPolygon | ShapelyMultiPolygon = None
    """Shapely Polygon of the constellation's boundary. Right ascension coordinates are in degrees (0...360)."""

    def __repr__(self) -> str:
        return f"Constellation(iau_id={self.iau_id}, name={self.name}, ra={self.ra}, dec={self.dec})"

    @classmethod
    def all(cls) -> Iterator["Constellation"]:
        df = constellations.load().to_pandas()

        for c in df.itertuples():
            yield from_tuple(c)

    @classmethod
    def get(cls, sql: str = None, **kwargs) -> "Constellation":
        """
        Get a Constellation, by matching its attributes.

        Example:

            hercules = Constellation.get(name="Hercules")

        Args:
            sql: SQL query for selecting constellation (table name is "_")
            **kwargs: Attributes on the constellation you want to match

        Raises: `ValueError` if more than one constellation is matched
        """
        filters = []

        for k, v in kwargs.items():
            filters.append(getattr(_, k) == v)

        df = constellations.load(filters=filters, sql=sql).to_pandas()
        results = [from_tuple(c) for c in df.itertuples()]

        if len(results) == 1:
            return results[0]

        if len(results) > 1:
            raise ValueError(
                "More than one match. Use find() instead or narrow your search."
            )

        return None

    @classmethod
    def find(cls, where: list = None, sql: str = None) -> list["Constellation"]:
        """
        Find Constellations

        Args:
            where: A list of expressions that determine which constellations to find. See [Selecting Objects](/reference-selecting-objects/) for details.
            sql: SQL query for selecting constellations (table name is "_")

        Returns:
            List of Constellations that match all `where` expressions

        """
        df = constellations.load(filters=where, sql=sql).to_pandas()

        return [from_tuple(c) for c in df.itertuples()]

    def constellation(self):
        """Not applicable to Constellation model, raises `NotImplementedError`"""
        raise NotImplementedError()


def from_tuple(c: tuple) -> Constellation:
    c = Constellation(
        ra=c.ra,
        dec=c.dec,
        iau_id=c.iau_id.lower(),
        name=c.name,
        star_hip_ids=c.star_hip_ids,
        boundary=c.geometry,
    )
    c._constellation_id = c.iau_id
    return c
