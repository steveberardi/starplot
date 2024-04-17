from typing import Optional

import numpy as np

from starplot.models.base import SkyObject, SkyObjectManager
from starplot.data.stars import StarCatalog, STAR_NAMES, load as _load_stars


class StarManager(SkyObjectManager):
    @classmethod
    def all(cls, catalog: StarCatalog = StarCatalog.HIPPARCOS):
        all_stars = _load_stars(catalog)

        # TODO : add datetime kwarg

        for s in all_stars.itertuples():
            hip_id = s.Index
            obj = Star(ra=s.ra_hours, dec=s.dec_degrees, magnitude=s.magnitude, bv=s.bv)

            if np.isfinite(hip_id):
                obj.hip = hip_id
                obj.name = STAR_NAMES.get(hip_id)

            yield obj


class Star(SkyObject):
    """
    Star model.
    """

    _manager = StarManager

    magnitude: float
    """Magnitude"""

    bv: Optional[float] = None
    """B-V Color Index, if available"""

    hip: Optional[int] = None
    """Hipparcos Catalog ID, if available"""

    name: Optional[str] = None
    """Name, if available"""

    def __init__(
        self,
        ra: float,
        dec: float,
        magnitude: float,
        bv: float = None,
        hip: int = None,
        name: str = None,
    ) -> None:
        super().__init__(ra, dec)
        self.magnitude = magnitude
        self.bv = bv
        self.hip = hip
        self.name = name

    @classmethod
    def get(**kwargs) -> "Star":
        """
        Get a Star, by matching its attributes.

        Example: `sirius = Star.get(name="Sirius")`

        Args:
            **kwargs: Attributes on the star you want to match

        Raises: `ValueError` if more than one star is matched
        """
        pass

    @classmethod
    def find(where: list) -> list["Star"]:
        """
        Find Stars

        Args:
            where: A list of expressions that determine which stars to find. See [Selecting Objects](/reference-selecting-objects/) for details.

        Returns:
            List of Stars that match all `where` expressions

        """
        pass
