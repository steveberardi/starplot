from dataclasses import dataclass
from typing import Optional, Union, Iterator

import numpy as np
from ibis import _
from shapely.geometry import Point

from starplot.models.base import SkyObject
from starplot.data.catalogs import Catalog, BIG_SKY_MAG11
from starplot.data.stars import load as _load_stars


@dataclass(slots=True, kw_only=True)
class Star(SkyObject):
    """
    Star model.
    """

    magnitude: float
    """Magnitude"""

    geometry: Point
    """Shapely Point of the star's position. Right ascension coordinates are in degrees (0...360)."""

    epoch_year: float = None
    """Epoch of position"""

    bv: Optional[float] = None
    """B-V Color Index, if available"""

    hip: Optional[int] = None
    """Hipparcos Catalog ID, if available"""

    tyc: Optional[str] = None
    """Tycho ID, if available"""

    ccdm: Optional[str] = None
    """CCDM Component Identifier (if applicable)"""

    parallax_mas: float = None
    """Trigonometric parallax in milliarcseconds"""

    ra_mas_per_year: float = None
    """Right ascension proper motion in milliarcseconds per Julian year"""

    dec_mas_per_year: float = None
    """Declination proper motion in milliarcseconds per Julian year"""

    name: Optional[str] = None
    """Name, if available"""

    bayer: Optional[str] = None
    """Bayer designation, if available"""

    flamsteed: Optional[int] = None
    """Flamsteed number, if available"""

    def __post_init__(self):
        self.bayer = self.bayer or None
        self.hip = (
            int(self.hip) if self.hip is not None and np.isfinite(self.hip) else None
        )
        self.flamsteed = (
            int(self.flamsteed)
            if self.flamsteed is not None and np.isfinite(self.flamsteed)
            else None
        )

    def __repr__(self) -> str:
        return f"Star(hip={self.hip}, tyc={self.tyc}, magnitude={self.magnitude}, ra={self.ra}, dec={self.dec})"

    @property
    def is_primary(self) -> bool:
        return not bool(self.ccdm) or self.ccdm.startswith("A")

    @classmethod
    def all(cls, catalog: Catalog = BIG_SKY_MAG11) -> Iterator["Star"]:
        """
        Get all stars from a catalog

        Args:
            catalog: Catalog you want to get star objects from

        Returns:
            Iterator of Star instances
        """
        df = _load_stars(catalog=catalog).to_pandas()

        for s in df.itertuples():
            yield from_tuple(s)

    @classmethod
    def get(
        cls, catalog: Catalog = BIG_SKY_MAG11, sql: str = None, **kwargs
    ) -> Union["Star", None]:
        """
        Get a Star, by matching its attributes as specified in `**kwargs`

        If there are multiple matches, then the first match (sorted by CCDM) will be returned.

        Example:

            sirius = Star.get(name="Sirius")

        Args:
            catalog: The catalog of stars to use
            sql: SQL query for selecting star (table name is "_")
            **kwargs: Attributes on the star you want to match

        Returns:
            First star that matches specified attributes, when sorted by CCDM -- or `None` if no star matches
        """
        filters = []

        for k, v in kwargs.items():
            filters.append(getattr(_, k) == v)

        table = _load_stars(
            catalog=catalog,
            filters=filters,
            sql=sql,
        )

        table = table.order_by(table.ccdm)
        df = table.to_pandas()

        results = [from_tuple(s) for s in df.itertuples()]

        if results:
            return results[0]

        return None

    @classmethod
    def find(
        cls,
        catalog: Catalog = BIG_SKY_MAG11,
        where: list = None,
        sql: str = None,
    ) -> list["Star"]:
        """
        Find Stars

        Args:
            catalog: The catalog of stars to use
            where: A list of expressions that determine which stars to find. See [Selecting Objects](/reference-selecting-objects/) for details.
            sql: SQL query for selecting stars (table name is "_")

        Returns:
            List of Stars that match all `where` expressions

        """
        # from ibis import to_sql

        # from starplot.data import db, DataFiles
        # con = db.connect()

        # exp = _load_stars(
        #     catalog=catalog,
        #     filters=where,
        #     sql=sql,
        # )

        # con.con.execute("INSTALL spatial; LOAD spatial;")
        # result = con.raw_sql(to_sql(exp))
        # # result = con.con.execute(to_sql(exp))
        # # result = con.con.execute(f"SELECT * FROM read_parquet('{DataFiles.BIG_SKY_MAG9}') where magnitude < 8")

        # rows =[]
        # while True:
        #     batch = result.fetchmany(5000)
        #     if not batch:
        #         break  # No more rows to fetch
        #     for row in batch:
        #         rows.append(row)

        # return rows

        df = _load_stars(
            catalog=catalog,
            filters=where,
            sql=sql,
        ).to_pandas()

        return [from_tuple(s) for s in df.itertuples()]

    @classmethod
    def get_label(cls, star) -> str:
        """
        Default function for determining the plotted label for a Star.

        Returns:
            The star's name
        """
        return star.name


def from_tuple(star: tuple) -> Star:
    s = Star(
        ra=star.ra,
        dec=star.dec,
        constellation_id=getattr(star, "constellation_id", None),
        magnitude=star.magnitude,
        hip=getattr(star, "hip", None),
        bv=getattr(star, "bv", None),
        tyc=getattr(star, "tyc_id", None),
        ccdm=getattr(star, "ccdm", None),
        parallax_mas=getattr(star, "parallax_mas", None),
        ra_mas_per_year=getattr(star, "ra_mas_per_year", None),
        dec_mas_per_year=getattr(star, "dec_mas_per_year", None),
        name=getattr(star, "name", None),
        bayer=getattr(star, "bayer", None),
        flamsteed=getattr(star, "flamsteed", None),
        geometry=star.geometry,
    )
    s._row_id = getattr(star, "rowid", None)

    # print(set(star._fields) )
    # populate extra fields
    # fields = Star._dir() + [
    #     'rowid',
    #     # 'sk',
    #     'Index',
    #     'constellation',
    #     'constellation_id',
    # ]
    # extra_fields = set(star._fields) - set(fields)
    # extra = {}
    # for f in extra_fields:
    #     # setattr(s, f, getattr(star, f))
    #     extra[f] = getattr(star, f)

    # s.extra = extra

    return s
