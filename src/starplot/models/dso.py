from typing import Optional

from starplot.data.dsos import DsoType
from starplot.mixins import CreateMapMixin, CreateOpticMixin
from starplot.models.base import SkyObject, SkyObjectManager


class DsoManager(SkyObjectManager):
    @classmethod
    def all(cls):
        from starplot.data.dsos import load_ongc, ONGC_TYPE_MAP

        all_dsos = load_ongc()

        for d in all_dsos.itertuples():
            magnitude = d.mag_v or d.mag_b or None
            magnitude = float(magnitude) if magnitude else None
            yield DSO(
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
            )


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
