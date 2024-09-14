from shapely import Polygon

from starplot.models.base import SkyObject, SkyObjectManager
from starplot.models.geometry import to_24h
from starplot.data import constellations


class ConstellationManager(SkyObjectManager):
    @classmethod
    def all(cls):
        all_constellations = constellations.load()
        for constellation in all_constellations.itertuples():
            yield from_tuple(constellation)


class Constellation(SkyObject):
    """
    Constellation model.
    """

    _manager = ConstellationManager

    iau_id: str = None
    """International Astronomical Union (IAU) three-letter designation, all lowercase"""

    name: str = None
    """Name"""

    boundary: Polygon = None
    """Shapely Polygon of the constellation's boundary. Right ascension coordinates are in 24H format."""

    def __init__(
        self,
        ra: float,
        dec: float,
        iau_id: str,
        name: str = None,
        boundary: Polygon = None,
    ) -> None:
        super().__init__(ra, dec)
        self.iau_id = iau_id.lower()
        self.name = name
        self.boundary = boundary

    def __repr__(self) -> str:
        return f"Constellation(iau_id={self.iau_id}, name={self.name}, ra={self.ra}, dec={self.dec})"

    @classmethod
    def get(**kwargs) -> "Constellation":
        """
        Get a Constellation, by matching its attributes.

        Example: `hercules = Constellation.get(name="Hercules")`

        Args:
            **kwargs: Attributes on the constellation you want to match

        Raises: `ValueError` if more than one constellation is matched
        """
        pass

    @classmethod
    def find(where: list) -> list["Constellation"]:
        """
        Find Constellations

        Args:
            where: A list of expressions that determine which constellations to find. See [Selecting Objects](/reference-selecting-objects/) for details.

        Returns:
            List of Constellations that match all `where` expressions

        """
        pass

    def constellation(self):
        """Not applicable to Constellation model, raises `NotImplementedError`"""
        raise NotImplementedError()


def from_tuple(c: tuple) -> Constellation:
    geometry = c.geometry
    if len(c.geometry.geoms) == 1:
        geometry = c.geometry.geoms[0]

    geometry = to_24h(geometry)

    return Constellation(
        ra=c.center_ra / 15,
        dec=c.center_dec,
        iau_id=c.iau_id,
        name=c.name,
        boundary=geometry,
    )
