from enum import Enum


ZENITH_BASE = [
    "M5",
    "M13",
    "M23",
    "M31",
    "M42",
    "M44",
    "M45",
    "M47",
    "M51",
    "M55",
    "M83",
    "M93",
    "M104",
]


class DsoType(str, Enum):
    """
    Types of deep sky objects (DSOs), as designated in OpenNGC
    """

    STAR = "Star"
    DOUBLE_STAR = "Double star"
    ASSOCIATION_OF_STARS = "Association of stars"

    OPEN_CLUSTER = "Open Cluster"
    GLOBULAR_CLUSTER = "Globular Cluster"

    GALAXY = "Galaxy"
    GALAXY_PAIR = "Galaxy Pair"
    GALAXY_TRIPLET = "Galaxy Triplet"
    GROUP_OF_GALAXIES = "Group of galaxies"

    NEBULA = "Nebula"
    PLANETARY_NEBULA = "Planetary Nebula"
    EMISSION_NEBULA = "Emission Nebula"
    STAR_CLUSTER_NEBULA = "Star cluster + Nebula"
    REFLECTION_NEBULA = "Reflection Nebula"

    DARK_NEBULA = "Dark Nebula"
    HII_IONIZED_REGION = "HII Ionized region"
    SUPERNOVA_REMNANT = "Supernova remnant"
    NOVA_STAR = "Nova star"
    NONEXISTENT = "Nonexistent object"
    UNKNOWN = "Object of other/unknown type"
    DUPLICATE_RECORD = "Duplicated record"


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

ONGC_TYPE_MAP = {v: k.value for k, v in ONGC_TYPE.items()}

DEFAULT_DSO_TYPES = [
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


def load_ongc(**kwargs):
    import geopandas as gpd
    import numpy as np
    from starplot.data import DataFiles

    all_dsos = gpd.read_file(
        DataFiles.ONGC.value,
        engine="pyogrio",
        use_arrow=True,
        **kwargs,
    )
    all_dsos = all_dsos.replace({np.nan: None})
    all_dsos = all_dsos[
        all_dsos["ra_degrees"].notnull() & all_dsos["dec_degrees"].notnull()
    ]
    return all_dsos
