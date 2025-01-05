from typing import Optional

import numpy as np
from shapely import Point

from starplot.models.base import SkyObject, SkyObjectManager
from starplot.data.stars import StarCatalog, STAR_NAMES, load as _load_stars


class StarManager(SkyObjectManager):
    @classmethod
    def all(cls, catalog: StarCatalog = StarCatalog.HIPPARCOS):
        all_stars = _load_stars(catalog)

        # TODO : add datetime kwarg

        for s in all_stars.itertuples():
            yield from_tuple(s, catalog)

    @classmethod
    def find(cls, where, catalog: StarCatalog = StarCatalog.HIPPARCOS):
        all_objects = cls.all(catalog)
        return super().find(where=where, all_objects=all_objects)

    @classmethod
    def get(cls, catalog: StarCatalog = StarCatalog.HIPPARCOS, **kwargs):
        all_objects = cls.all(catalog)
        return super().get(all_objects=all_objects, **kwargs)


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

    tyc: Optional[str] = None
    """Tycho ID, if available"""

    ccdm: Optional[str] = None
    """CCDM Component Identifier (if applicable)"""

    name: Optional[str] = None
    """Name, if available"""

    geometry: Point = None
    """Shapely Point of the star's position. Right ascension coordinates are in 24H format."""

    def __init__(
        self,
        ra: float,
        dec: float,
        magnitude: float,
        bv: float = None,
        hip: int = None,
        name: str = None,
        tyc: str = None,
        ccdm: str = None,
        geometry: Point = None,
    ) -> None:
        super().__init__(ra, dec)
        self.magnitude = magnitude
        self.bv = bv
        self.hip = hip if hip is not None and np.isfinite(hip) else None
        self.name = name
        self.tyc = tyc
        self.ccdm = ccdm
        self.geometry = geometry

    def __repr__(self) -> str:
        return f"Star(hip={self.hip}, tyc={self.tyc}, magnitude={self.magnitude}, ra={self.ra}, dec={self.dec})"

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


def from_tuple(star: tuple) -> Star:
    ra, dec = star.ra_hours, star.dec_degrees

    hip = getattr(star, "hip", None)

    s = Star(
        ra=ra,
        dec=dec,
        hip=hip,
        magnitude=star.magnitude,
        bv=getattr(star, "bv", None),
        tyc=getattr(star, "tyc_id", None),
        ccdm=getattr(star, "ccdm", None),
        name=getattr(star, "name", None),
        geometry=star.geometry,
    )
    s._row_id = getattr(star, "rowid", None),

    if s._row_id:
        s._row_id = s._row_id[0]

    return s
