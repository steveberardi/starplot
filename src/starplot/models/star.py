import math
from typing import Optional, Union, Iterator, Any

import numpy as np
from ibis import _
from pydantic import field_validator

from starplot.models.base import SkyObject, ShapelyPoint
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

    geometry: ShapelyPoint = None
    """Shapely Point of the star's position. Right ascension coordinates are in degrees (0...360)."""

    @field_validator("flamsteed", "hip", mode="before")
    @classmethod
    def nan(cls, value: int) -> int:
        if not value or math.isnan(value):
            return None

        return int(value)

    def model_post_init(self, context: Any) -> None:
        self.bayer = self.bayer or None
        self.hip = self.hip if self.hip is not None and np.isfinite(self.hip) else None

    def __repr__(self) -> str:
        return f"Star(hip={self.hip}, tyc={self.tyc}, magnitude={self.magnitude}, ra={self.ra}, dec={self.dec})"

    @classmethod
    def all(cls, catalog: StarCatalog = StarCatalog.BIG_SKY_MAG11) -> Iterator["Star"]:
        df = _load_stars(catalog=catalog).to_pandas()

        for s in df.itertuples():
            yield from_tuple(s)

    @classmethod
    def get(
        cls, catalog: StarCatalog = StarCatalog.BIG_SKY_MAG11, sql: str = None, **kwargs
    ) -> Union["Star", None]:
        """
        Get a Star, by matching its attributes as specified in `**kwargs`

        Example:

            sirius = Star.get(name="Sirius")

        Args:
            catalog: The catalog of stars to use: "big-sky-mag11", or "big-sky" -- see [`StarCatalog`](/reference-data/#starplot.data.stars.StarCatalog) for details
            sql: SQL query for selecting star (table name is "_")
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
            sql=sql,
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
        cls,
        where: list = None,
        sql: str = None,
        catalog: StarCatalog = StarCatalog.BIG_SKY_MAG11,
    ) -> list["Star"]:
        """
        Find Stars

        Args:
            where: A list of expressions that determine which stars to find. See [Selecting Objects](/reference-selecting-objects/) for details.
            sql: SQL query for selecting stars (table name is "_")
            catalog: The catalog of stars to use: "big-sky-mag11", or "big-sky" -- see [`StarCatalog`](/reference-data/#starplot.data.stars.StarCatalog) for details

        Returns:
            List of Stars that match all `where` expressions

        """
        df = _load_stars(
            catalog=catalog,
            filters=where,
            sql=sql,
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
        bayer=getattr(star, "bayer", None),
        flamsteed=getattr(star, "flamsteed", None),
    )
    s._constellation_id = getattr(star, "constellation", None)
    s._row_id = getattr(star, "rowid", None)

    return s
