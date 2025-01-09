import numpy as np
import ibis
from ibis import _

from starplot.data import db


class DsoType:
    """
    Types of deep sky objects (DSOs), as designated in OpenNGC
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

BASIC_DSO_TYPES = [
    # Star Clusters ----------
    DsoType.OPEN_CLUSTER,
    DsoType.GLOBULAR_CLUSTER,
    # Galaxies ----------
    DsoType.GALAXY,
    DsoType.GALAXY_PAIR,
    DsoType.GALAXY_TRIPLET,
    DsoType.GROUP_OF_GALAXIES,
    # Nebulas ----------
    DsoType.NEBULA,
    DsoType.PLANETARY_NEBULA,
    DsoType.EMISSION_NEBULA,
    DsoType.STAR_CLUSTER_NEBULA,
    DsoType.REFLECTION_NEBULA,
    # Stars ----------
    # DsoType.DOUBLE_STAR,
    DsoType.ASSOCIATION_OF_STARS,
]
"""Default types of Deep Sky Objects (DSOs) that are plotted when you call `dsos()` on a plot"""

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


class DsoLabelMaker(dict):
    """
    This is pretty hacky, but it helps keep a consistent interface for plotting labels and any overrides.

    Basically this is just a dictionary that returns the key itself for any get() call, unless
    the key is present in the 'overrides' dict that's passed on init
    """

    def __init__(self, *args, **kwargs):
        self._overrides = kwargs.get("overrides") or {}

    def __getitem__(self, key):
        return self.get(key)

    def get(self, key):
        return self._overrides.get(key) or key


DSO_LABELS_DEFAULT = DsoLabelMaker()


def load(extent=None, filters=None):
    filters = filters or []
    con = db.connect()
    dsos = con.table("deep_sky_objects")

    dsos = dsos.mutate(
        magnitude=ibis.coalesce(_.mag_v, _.mag_b, None),
        rowid=ibis.row_number(),
        size=_.size_deg2,
    )

    if extent:
        dsos = dsos.filter(_.geometry.intersects(extent))

    filters.extend([_.ra_degrees.notnull() & _.dec_degrees.notnull()])

    if filters:
        return dsos.filter(*filters)

    return dsos
