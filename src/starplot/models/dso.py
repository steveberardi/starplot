from typing import Optional, Union, Iterator

from ibis import _
from shapely.geometry import Polygon, MultiPolygon

from starplot.data.dsos import load
from starplot.mixins import CreateMapMixin, CreateOpticMixin
from starplot.models.base import SkyObject


class DsoType:
    """
    Type of deep sky object (DSOs), as designated in OpenNGC
    """

    STAR = "*"
    DOUBLE_STAR = "**"
    ASSOCIATION_OF_STARS = "*Ass"
    OPEN_CLUSTER = "OCl"
    GLOBULAR_CLUSTER = "GCl"
    GALAXY = "G"
    GALAXY_PAIR = "GPair"
    GALAXY_TRIPLET = "GTrpl"
    GROUP_OF_GALAXIES = "GGroup"
    NEBULA = "Neb"
    PLANETARY_NEBULA = "PN"
    EMISSION_NEBULA = "EmN"
    STAR_CLUSTER_NEBULA = "Cl+N"
    REFLECTION_NEBULA = "RfN"
    DARK_NEBULA = "DrkN"
    HII_IONIZED_REGION = "HII"
    SUPERNOVA_REMNANT = "SNR"
    NOVA_STAR = "Nova"
    NONEXISTENT = "NonEx"
    UNKNOWN = "Other"
    DUPLICATE_RECORD = "Dup"


class DSO(SkyObject, CreateMapMixin, CreateOpticMixin):
    """
    Deep Sky Object (DSO) model. An instance of this model is passed to any [callables](/reference-callables) you define when plotting DSOs.
    So, you can use any attributes of this model in your callables. Note that some may be null.
    """

    name: str
    """Name of the DSO (as specified in OpenNGC)"""

    type: DsoType
    """Type of DSO"""

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
    """Shapely Polygon of the DSO's extent. Right ascension coordinates are in degrees (0...360)."""

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
        constellation_id: str = None,
    ) -> None:
        super().__init__(ra, dec, constellation_id)
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
    def all(cls) -> Iterator["DSO"]:
        df = load().to_pandas()

        for d in df.itertuples():
            yield from_tuple(d)

    @classmethod
    def get(cls, **kwargs) -> "DSO":
        """
        Get a DSO, by matching its attributes.

        Example:

            d = DSO.get(m=13)

        Args:
            **kwargs: Attributes on the DSO you want to match

        Raises: `ValueError` if more than one DSO is matched
        """
        filters = []

        for k, v in kwargs.items():
            filters.append(getattr(_, k) == v)

        df = load(filters=filters).to_pandas()

        results = [from_tuple(d) for d in df.itertuples()]

        if len(results) == 1:
            return results[0]

        if len(results) > 1:
            raise ValueError(
                "More than one match. Use find() instead or narrow your search."
            )

        return None

    @classmethod
    def find(cls, where: list) -> list["DSO"]:
        """
        Find DSOs

        Args:
            where: A list of expressions that determine which DSOs to find. See [Selecting Objects](/reference-selecting-objects/) for details.

        Returns:
            List of DSOs that match all `where` expressions

        """
        df = load(filters=where).to_pandas()
        return [from_tuple(d) for d in df.itertuples()]


def from_tuple(d: tuple) -> DSO:
    dso = DSO(
        name=d.name,
        ra=d.ra,
        dec=d.dec,
        type=d.type,
        maj_ax=d.maj_ax,
        min_ax=d.min_ax,
        angle=d.angle,
        magnitude=d.magnitude,
        size=d.size,
        m=d.m,
        ngc=d.ngc,
        ic=d.ic,
        geometry=d.geometry,
        constellation_id=d.constellation_id,
    )
    dso._row_id = getattr(d, "rowid", None)
    return dso


ONGC_TYPE = {
    # Star Clusters ----------
    DsoType.OPEN_CLUSTER: "OCl",
    DsoType.GLOBULAR_CLUSTER: "GCl",
    # Galaxies ----------
    DsoType.GALAXY: "G",
    DsoType.GALAXY_PAIR: "GPair",
    DsoType.GALAXY_TRIPLET: "GTrpl",
    DsoType.GROUP_OF_GALAXIES: "GGroup",
    # Nebulas ----------
    DsoType.NEBULA: "Neb",
    DsoType.PLANETARY_NEBULA: "PN",
    DsoType.EMISSION_NEBULA: "EmN",
    DsoType.STAR_CLUSTER_NEBULA: "Cl+N",
    DsoType.REFLECTION_NEBULA: "RfN",
    # Stars ----------
    DsoType.STAR: "*",
    DsoType.DOUBLE_STAR: "**",
    DsoType.ASSOCIATION_OF_STARS: "*Ass",
    # Others
    DsoType.HII_IONIZED_REGION: "HII",
    DsoType.DARK_NEBULA: "DrkN",
    DsoType.SUPERNOVA_REMNANT: "SNR",
    DsoType.NOVA_STAR: "Nova",
    DsoType.NONEXISTENT: "NonEx",
    DsoType.UNKNOWN: "Other",
    DsoType.DUPLICATE_RECORD: "Dup",
}

ONGC_TYPE_MAP = {v: k for k, v in ONGC_TYPE.items()}

DSO_LEGEND_LABELS = {
    # Galaxies ----------
    DsoType.GALAXY: "Galaxy",
    DsoType.GALAXY_PAIR: "Galaxy",
    DsoType.GALAXY_TRIPLET: "Galaxy",
    DsoType.GROUP_OF_GALAXIES: "Galaxy",
    # Nebulas ----------
    DsoType.NEBULA: "Nebula",
    DsoType.PLANETARY_NEBULA: "Nebula",
    DsoType.EMISSION_NEBULA: "Nebula",
    DsoType.STAR_CLUSTER_NEBULA: "Nebula",
    DsoType.REFLECTION_NEBULA: "Nebula",
    # Star Clusters ----------
    DsoType.OPEN_CLUSTER: "Open Cluster",
    DsoType.GLOBULAR_CLUSTER: "Globular Cluster",
    # Stars ----------
    DsoType.DOUBLE_STAR: "Double Star",
    DsoType.ASSOCIATION_OF_STARS: "Association of stars",
    DsoType.NOVA_STAR: "Nova Star",
    # Others
    DsoType.HII_IONIZED_REGION: "HII Ionized Region",
    DsoType.DARK_NEBULA: "Dark Nebula",
    DsoType.SUPERNOVA_REMNANT: "Supernova Remnant",
}
