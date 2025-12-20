from dataclasses import dataclass
from typing import Optional, Iterator
from enum import Enum

from ibis import _
from shapely import Polygon, MultiPolygon

from starplot.data.catalogs import Catalog, OPEN_NGC
from starplot.data.dsos import load
from starplot.models.base import SkyObject


class DsoType(str, Enum):
    """
    Type of deep sky object (DSO), as designated in OpenNGC
    """

    STAR = "*"
    """Star"""

    DOUBLE_STAR = "**"
    """Double star or multiple star system"""

    ASSOCIATION_OF_STARS = "*Ass"
    """Association of stars"""

    OPEN_CLUSTER = "OCl"
    """Open cluster of stars"""

    GLOBULAR_CLUSTER = "GCl"
    """Globular cluster of stars"""

    GALAXY = "G"
    """Galaxy"""

    GALAXY_PAIR = "GPair"
    """Group of two galaxies"""

    GALAXY_TRIPLET = "GTrpl"
    """Group of three galaxies"""

    GROUP_OF_GALAXIES = "GGroup"
    """Group of more than three galaxies"""

    NEBULA = "Neb"
    """Nebula"""

    PLANETARY_NEBULA = "PN"
    """Planetary nebula"""

    EMISSION_NEBULA = "EmN"
    """Emission Nebula"""

    STAR_CLUSTER_NEBULA = "Cl+N"
    """Star cluster with nebulosity"""

    REFLECTION_NEBULA = "RfN"
    """Reflection nebula"""

    DARK_NEBULA = "DrkN"
    """Dark nebula"""

    HII_IONIZED_REGION = "HII"
    """Hydrogen ionized region"""

    SUPERNOVA_REMNANT = "SNR"
    """Supernova remnant"""

    NOVA_STAR = "Nova"
    """Nova star"""

    NONEXISTENT = "NonEx"
    """Non-existant object"""

    UNKNOWN = "Other"
    """Unknown type of object"""

    DUPLICATE_RECORD = "Dup"
    """Duplicate record of another object"""


@dataclass(slots=True, kw_only=True)
class DSO(SkyObject):
    """
    Deep Sky Object (DSO) model. An instance of this model is passed to any [callables](/reference-callables) you define when plotting DSOs.
    So, you can use any attributes of this model in your callables. Note that some may be null.
    """

    name: str = None
    """Name of the DSO (as specified in OpenNGC)"""

    type: DsoType = DsoType.UNKNOWN
    """Type of DSO"""

    common_names: list[str] = None
    """
    List of common names for the DSO (e.g. 'Andromeda Galaxy' for M31)
    
    Note: this field is parsed into a list of strings _after_ querying DSOs, so if you want to query on this field, you should treat it as a comma-separated list.
    """

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

    geometry: Polygon | MultiPolygon = None
    """Shapely Polygon of the DSO's extent. Right ascension coordinates are in degrees (0...360)."""

    def __repr__(self) -> str:
        return f"DSO(name={self.name}, magnitude={self.magnitude})"

    @classmethod
    def all(cls, catalog: Catalog = OPEN_NGC) -> Iterator["DSO"]:
        """
        Get all DSOs from a catalog

        Args:
            catalog: Catalog you want to get DSO objects from

        Returns:
            Iterator of DSO instances
        """
        df = load(catalog=catalog).to_pandas()

        for d in df.itertuples():
            yield from_tuple(d)

    @classmethod
    def get(cls, catalog: Catalog = OPEN_NGC, sql: str = None, **kwargs) -> "DSO":
        """
        Get a DSO, by matching its attributes.

        Example:

            d = DSO.get(m=13)

        Args:
            catalog: Catalog you want to search
            sql: SQL query for selecting DSO (table name is "_")
            **kwargs: Attributes on the DSO you want to match

        Raises: `ValueError` if more than one DSO is matched
        """
        filters = []

        for k, v in kwargs.items():
            filters.append(getattr(_, k) == v)

        df = load(catalog=catalog, filters=filters, sql=sql).to_pandas()

        results = [from_tuple(d) for d in df.itertuples()]

        if len(results) == 1:
            return results[0]

        if len(results) > 1:
            raise ValueError(
                "More than one match. Use find() instead or narrow your search."
            )

        return None

    @classmethod
    def find(
        cls, catalog: Catalog = OPEN_NGC, where: list = None, sql: str = None
    ) -> list["DSO"]:
        """
        Find DSOs

        Args:
            catalog: Catalog you want to search
            where: A list of expressions that determine which DSOs to find. See [Selecting Objects](/reference-selecting-objects/) for details.
            sql: SQL query for selecting DSOs (table name is "_")

        Returns:
            List of DSOs that match all `where` expressions

        """
        df = load(catalog=catalog, filters=where, sql=sql).to_pandas()
        return [from_tuple(d) for d in df.itertuples()]

    @classmethod
    def get_label(cls, dso) -> str:
        """
        Default function for determining the plotted label for a DSO.

        Returns:

        1. `"M13"` if DSO is a Messier object
        2. `"6456"` if DSO is an NGC object
        3. `"IC1920"` if DSO is an IC object
        4. Empty string otherwise

        """
        if dso.m:
            return f"M{dso.m}"

        if dso.ngc:
            return f"{dso.ngc}"

        if dso.ic:
            return f"IC{dso.ic}"

        return ""


def from_tuple(d: tuple) -> DSO:
    dso = DSO(
        ra=d.ra,
        dec=d.dec,
        constellation_id=d.constellation_id,
        name=d.name,
        common_names=d.common_names.split(",") if d.common_names else [],
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
    DsoType.PLANETARY_NEBULA: "Planetary Nebula",
    DsoType.EMISSION_NEBULA: "Nebula",
    DsoType.STAR_CLUSTER_NEBULA: "Nebula",
    DsoType.REFLECTION_NEBULA: "Nebula",
    DsoType.HII_IONIZED_REGION: "Nebula",
    # Star Clusters ----------
    DsoType.OPEN_CLUSTER: "Open Cluster",
    DsoType.GLOBULAR_CLUSTER: "Globular Cluster",
    # Stars ----------
    DsoType.DOUBLE_STAR: "Double Star",
    DsoType.ASSOCIATION_OF_STARS: "Association of stars",
    DsoType.NOVA_STAR: "Nova Star",
    # Others
    DsoType.DARK_NEBULA: "Dark Nebula",
    DsoType.SUPERNOVA_REMNANT: "Supernova Remnant",
}
