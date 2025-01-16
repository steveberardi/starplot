import math
from typing import Optional, Union, Iterator

import numpy as np
from shapely import Point
from ibis import _

from starplot.models.base import SkyObject
from starplot.data.stars import StarCatalog, load as _load_stars


class Star(SkyObject):
    """
    Star model.
    """

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

    bayer: Optional[str] = None
    """Bayer designation, if available"""

    flamsteed: Optional[int] = None
    """Flamsteed number, if available"""

    geometry: Point = None
    """Shapely Point of the star's position. Right ascension coordinates are in degrees (0...360)."""

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
        constellation_id: str = None,
        bayer: str = None,
        flamsteed: int = None,
    ) -> None:
        super().__init__(ra, dec, constellation_id)
        self.magnitude = magnitude
        self.bv = bv
        self.hip = hip if hip is not None and np.isfinite(hip) else None
        self.name = name
        self.tyc = tyc
        self.ccdm = ccdm
        self.geometry = geometry

        if bayer:
            self.bayer = bayer

        if flamsteed and not math.isnan(flamsteed):
            self.flamsteed = int(flamsteed)

    def __repr__(self) -> str:
        return f"Star(hip={self.hip}, tyc={self.tyc}, magnitude={self.magnitude}, ra={self.ra}, dec={self.dec})"

    @classmethod
    def all(cls, catalog: StarCatalog = StarCatalog.BIG_SKY_MAG11) -> Iterator["Star"]:
        df = _load_stars(catalog=catalog).to_pandas()

        for s in df.itertuples():
            yield from_tuple(s)

    @classmethod
    def get(
        cls, catalog: StarCatalog = StarCatalog.BIG_SKY_MAG11, **kwargs
    ) -> Union["Star", None]:
        """
        Get a Star, by matching its attributes as specified in `**kwargs`

        Example:

            sirius = Star.get(name="Sirius")

        Args:
            catalog: The catalog of stars to use: "big-sky-mag11", or "big-sky" -- see [`StarCatalog`](/reference-data/#starplot.data.stars.StarCatalog) for details
            **kwargs: Attributes on the star you want to match

        Raises: `ValueError` if more than one star is matched

        Returns:
            Star instance if there's exactly one match or `None` if there are zero matches
        """
        filters = []

        for k, v in kwargs.items():
            filters.append(getattr(_, k) == v)

        df = _load_stars(
            catalog=catalog,
            filters=filters,
        ).to_pandas()

        results = [from_tuple(s) for s in df.itertuples()]

        if len(results) == 1:
            return results[0]

        if len(results) > 1:
            raise ValueError(
                "More than one match. Use find() instead or narrow your search."
            )

        return None

    @classmethod
    def find(
        cls, where: list, catalog: StarCatalog = StarCatalog.BIG_SKY_MAG11
    ) -> list["Star"]:
        """
        Find Stars

        Args:
            where: A list of expressions that determine which stars to find. See [Selecting Objects](/reference-selecting-objects/) for details.
            catalog: The catalog of stars to use: "big-sky-mag11", or "big-sky" -- see [`StarCatalog`](/reference-data/#starplot.data.stars.StarCatalog) for details

        Returns:
            List of Stars that match all `where` expressions

        """
        df = _load_stars(
            catalog=catalog,
            filters=where,
        ).to_pandas()

        return [from_tuple(s) for s in df.itertuples()]


def from_tuple(star: tuple) -> Star:
    s = Star(
        ra=star.ra,
        dec=star.dec,
        hip=getattr(star, "hip", None),
        magnitude=star.magnitude,
        bv=getattr(star, "bv", None),
        tyc=getattr(star, "tyc_id", None),
        ccdm=getattr(star, "ccdm", None),
        name=getattr(star, "name", None),
        geometry=star.geometry,
        constellation_id=getattr(star, "constellation", None),
        bayer=getattr(star, "bayer", None),
        flamsteed=getattr(star, "flamsteed", None),
    )
    s._row_id = getattr(star, "rowid", None)

    return s
