from starplot.models.base import SkyObject, SkyObjectManager
from starplot.data import constellations


class ConstellationManager(SkyObjectManager):
    @classmethod
    def all(cls):
        for iau_id in constellations.iterator():
            name, ra, dec = constellations.get(iau_id)
            yield Constellation(
                ra=ra, dec=dec, iau_id=iau_id, name=name.replace("\n", " ")
            )


class Constellation(SkyObject):
    """
    Constellation model.
    """

    _manager = ConstellationManager

    iau_id: str = None
    """International Astronomical Union (IAU) three-letter designation, all lowercase"""

    name: str = None
    """Name"""

    def __init__(
        self,
        ra: float,
        dec: float,
        iau_id: str,
        name: str = None,
    ) -> None:
        super().__init__(ra, dec)
        self.iau_id = iau_id.lower()
        self.name = name

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
