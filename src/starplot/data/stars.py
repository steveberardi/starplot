from enum import Enum

from pandas import read_parquet

from starplot.data import DataFiles

"""
    Dictionary of stars that will be labeled on the plot

    Keys: Hipparcos ID
    Values: Common Name
"""

hip_names = {
    7588: "Achernar",
    60718: "Acrux",
    33579: "Adhara",
    68702: "Hadar",
    95947: "Albireo",
    65477: "Alcor",
    17702: "Alcyone",
    21421: "Aldebaran",
    105199: "Alderamin",
    15863: "Mirfak",
    50583: "Algieba",
    14576: "Algol",
    31681: "Alhena",
    62956: "Alioth",
    67301: "Benetnash",
    9640: "Almach",
    109268: "Alnair",
    26311: "Alnilam",
    26727: "Alnitak",
    46390: "Alphard",
    76267: "Gemma",
    677: "Sirrah",
    97649: "Altair",
    35904: "Aludra",
    2081: "Ankaa",
    80763: "Antares",
    69673: "Arcturus",
    102098: "Deneb",
    45556: "Turais",
    82273: "Atria",
    41037: "Avior",
    62434: "Mimosa",
    25336: "Bellatrix",
    27989: "Betelgeuse",
    66657: "Birdun",
    30438: "Canopus",
    24608: "Capella",
    746: "Caph",
    36850: "Castor",
    3419: "Diphda",
    57632: "Denebola",
    78401: "Dschubba",
    54061: "Dubhe",
    8102: "Durre Menthor",
    25428: "Elnath",
    107315: "Enif",
    87833: "Etamin",
    113368: "Fomalhaut",
    93308: "Tseen She",
    61084: "Gacrux",
    102488: "Gienah",
    86228: "Sargas",
    112122: "Gruid",
    9884: "Hamal",
    107259: "Herschel's Garnet Star",
    72105: "Izar",
    90185: "Kaus Australis",
    72607: "Kochab",
    42913: "Koo She",
    113963: "Marchab",
    71352: "Marfikent",
    45941: "Markab",
    59774: "Megrez",
    71860: "Men",
    28360: "Menkalinan",
    68933: "Menkent",
    53910: "Merak",
    45238: "Miaplacidus",
    25930: "Mintaka",
    10826: "Mira",
    5447: "Mirach",
    30324: "Murzim",
    65378: "Mizar",
    61932: "Muhlifein",
    39429: "Naos",
    92855: "Nunki",
    100751: "Peacock",
    58001: "Phecda",
    11767: "Polaris",
    37826: "Pollux",
    37279: "Procyon",
    86032: "Rasalhague",
    39953: "Regor",
    49669: "Regulus",
    24436: "Rigel",
    71683: "Toliman",
    84012: "Sabik",
    16537: "Sadira",
    100453: "Sadr",
    27366: "Saiph",
    113881: "Scheat",
    3179: "Schedar",
    85927: "Shaula",
    32349: "Sirius",
    104382: "South Star",
    65474: "Spica",
    44816: "Suhail",
    68756: "Thuban",
    4427: "Tsih",
    91262: "Vega",
    82396: "Wei",
    34444: "Wezen",
}

ZENITH_BASE = [
    95947,
    65477,
    21421,
    62956,
    46390,
    677,
    97649,
    80763,
    69673,
    27989,
    30438,
    24608,
    36850,
    102098,
    3419,
    54061,
    25428,
    113368,
    65378,
    11767,
    37826,
    37279,
    49669,
    24436,
    85927,
    32349,
    65474,
    91262,
]

BASE_LIMITING_MAG = 8


class StarCatalog(str, Enum):
    """Built-in star catalogs"""

    HIPPARCOS = "hipparcos"
    """Hipparcos Catalog = 118,218 stars"""

    TYCHO_1 = "tycho-1"
    """Tycho-1 Catalog = 1,055,115 stars"""


def load_hipparcos():
    return read_parquet(DataFiles.HIPPARCOS)


def load_tycho1():
    # columns=[
    #     "hip",
    #     "magnitude",
    #     "ra_hours",
    #     "dec_degrees",
    #     "parallax_mas",
    #     "ra_mas_per_year",
    #     "dec_mas_per_year",
    #     "bv",
    # ]
    df = read_parquet(DataFiles.TYCHO_1)
    df = df.assign(
        ra_degrees=df["ra_hours"] * 15.0,
        epoch_year=1991.25,
    )
    return df.set_index("hip")


def load(catalog: StarCatalog = StarCatalog.HIPPARCOS):
    if catalog == StarCatalog.TYCHO_1:
        return load_tycho1()
    elif catalog == StarCatalog.HIPPARCOS:
        return load_hipparcos()
    else:
        raise ValueError("Unrecognized star catalog.")
