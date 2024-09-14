from typing import Optional, Union

from shapely.geometry import Polygon, MultiPolygon

from starplot.data.dsos import DsoType, load_ongc, ONGC_TYPE_MAP
from starplot.mixins import CreateMapMixin, CreateOpticMixin
from starplot.models.base import SkyObject, SkyObjectManager
from starplot.models.geometry import to_24h
from starplot import geod


class DsoManager(SkyObjectManager):
    @classmethod
    def all(cls):
        all_dsos = load_ongc()

        for d in all_dsos.itertuples():
            magnitude = d.mag_v or d.mag_b or None
            magnitude = float(magnitude) if magnitude else None
            yield from_tuple(d)


class DSO(SkyObject, CreateMapMixin, CreateOpticMixin):
    """
    Deep Sky Object (DSO) model. An instance of this model is passed to any [callables](/reference-callables) you define when plotting DSOs.
    So, you can use any attributes of this model in your callables. Note that some may be null.
    """

    _manager = DsoManager

    name: str
    """Name of the DSO (as specified in OpenNGC)"""

    type: DsoType

    magnitude: Optional[float] = None
    """Magnitude (if available)"""

    maj_ax: Optional[float] = None
    """Major axis of the DSO, in arcmin (if available)"""

    min_ax: Optional[float] = None
    """Minor axis of the DSO, in arcmin (if available)"""

    angle: Optional[float] = None
    """Angle of the DSO, in degrees (if available)"""

    size: Optional[float] = None
    """Size of the DSO calculated as the area of the minimum bounding rectangle of the DSO, in degrees squared (if available)"""

    m: Optional[str] = None
    """
    Messier number. *Note that this field is a string, to be consistent with the other identifier fields (`ngc` and `ic`).*
    """

    ngc: Optional[str] = None
    """
    New General Catalogue (NGC) identifier. *Note that this field is a string, to support objects like '3537 NED01'.*
    """

    ic: Optional[str] = None
    """
    Index Catalogue (IC) identifier. *Note that this field is a string, to support objects like '4974 NED01'.*
    """

    geometry: Union[Polygon, MultiPolygon] = None
    """Shapely Polygon of the DSO's extent. Right ascension coordinates are in 24H format."""

    def __init__(
        self,
        ra: float,
        dec: float,
        name: str,
        type: DsoType,
        magnitude: float = None,
        maj_ax: float = None,
        min_ax: float = None,
        angle: float = None,
        size: float = None,
        m: str = None,
        ngc: str = None,
        ic: str = None,
        geometry: Union[Polygon, MultiPolygon] = None,
    ) -> None:
        super().__init__(ra, dec)
        self.name = name
        self.type = type
        self.magnitude = magnitude
        self.maj_ax = maj_ax
        self.min_ax = min_ax
        self.angle = angle
        self.size = size
        self.m = m
        self.ngc = ngc
        self.ic = ic
        self.geometry = geometry

    def __repr__(self) -> str:
        return f"DSO(name={self.name}, magnitude={self.magnitude})"

    @classmethod
    def get(**kwargs) -> "DSO":
        """
        Get a DSO, by matching its attributes.

        Example: `d = DSO.get(m=13)`

        Args:
            **kwargs: Attributes on the DSO you want to match

        Raises: `ValueError` if more than one DSO is matched
        """
        pass

    @classmethod
    def find(where: list) -> list["DSO"]:
        """
        Find DSOs

        Args:
            where: A list of expressions that determine which DSOs to find. See [Selecting Objects](/reference-selecting-objects/) for details.

        Returns:
            List of DSOs that match all `where` expressions

        """
        pass


def create_ellipse(d):
    maj_ax, min_ax, angle = d.maj_ax, d.min_ax, d.angle

    if maj_ax is None:
        return d.geometry

    if angle is None:
        angle = 0

    maj_ax_degrees = (maj_ax / 60) / 2

    if not min_ax:
        min_ax_degrees = maj_ax_degrees
    else:
        min_ax_degrees = (min_ax / 60) / 2

    points = geod.ellipse(
        (d.ra_degrees / 15, d.dec_degrees),
        min_ax_degrees * 2,
        maj_ax_degrees * 2,
        angle,
        num_pts=100,
    )

    # points = [geod.to_radec(p) for p in points]
    points = [(round(ra, 4), round(dec, 4)) for ra, dec in points]
    return Polygon(points)


def from_tuple(d: tuple) -> DSO:
    magnitude = d.mag_v or d.mag_b or None
    magnitude = float(magnitude) if magnitude else None
    geometry = d.geometry

    if str(geometry.geom_type) not in ["Polygon", "MultiPolygon"]:
        geometry = create_ellipse(d)

    geometry = to_24h(geometry)

    return DSO(
        name=d.name,
        ra=d.ra_degrees / 15,
        dec=d.dec_degrees,
        type=ONGC_TYPE_MAP[d.type],
        maj_ax=d.maj_ax,
        min_ax=d.min_ax,
        angle=d.angle,
        magnitude=magnitude,
        size=d.size_deg2,
        m=d.m,
        ngc=d.ngc,
        ic=d.ic,
        geometry=geometry,
    )
