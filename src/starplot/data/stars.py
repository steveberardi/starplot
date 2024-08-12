from enum import Enum

from pandas import read_parquet

from starplot.data import bigsky, DataFiles

STAR_NAMES = {
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
"""Star names by their HIP id. You can override these values when calling `stars()`"""


class StarCatalog(str, Enum):
    """Built-in star catalogs"""

    HIPPARCOS = "hipparcos"
    """Hipparcos Catalog = 118,218 stars"""

    BIG_SKY_MAG11 = "big-sky-mag11"
    """
    [Big Sky Catalog](https://github.com/steveberardi/bigsky) ~ 900k stars up to magnitude 11
    
    This is an _abridged_ version of the Big Sky Catalog, including stars up to a limiting magnitude of 11 (total = 981,852).

    This catalog is included with Starplot, so does not require downloading any files.
    """

    BIG_SKY = "big-sky"
    """
    [Big Sky Catalog](https://github.com/steveberardi/bigsky) ~ 2.5M stars

    This is the full version of the Big Sky Catalog, which includes 2,557,499 stars from Hipparcos, Tycho-1, and Tycho-2.

    This catalog is very large (50+ MB), so it's not built-in to Starplot. When you plot stars and specify this catalog, the catalog 
    will be downloaded from the [Big Sky GitHub repository](https://github.com/steveberardi/bigsky) and saved to Starplot's data library 
    directory. You can override this download path with the environment variable `STARPLOT_DOWNLOAD_PATH`
    
    """


def load_bigsky():
    if not bigsky.exists():
        bigsky.download()

    return bigsky.load(DataFiles.BIG_SKY)


def load(catalog: StarCatalog = StarCatalog.HIPPARCOS):
    if catalog == StarCatalog.HIPPARCOS:
        return read_parquet(DataFiles.HIPPARCOS)
    elif catalog == StarCatalog.BIG_SKY_MAG11:
        return bigsky.load(DataFiles.BIG_SKY_MAG11)
    elif catalog == StarCatalog.BIG_SKY:
        return bigsky.load(DataFiles.BIG_SKY)
    else:
        raise ValueError("Unrecognized star catalog.")
