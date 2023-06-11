from skyfield.api import load
from skyfield.data import hipparcos


"""
    Dictionary of stars that will be labeled on the plot

    Keys: Hipparcos ID
    Values: Common Name
"""
star_names = {
    95947: "Albireo",
    65477: "Alcor",
    21421: "Aldebaran",
    62956: "Alioth",
    46390: "Alphard",
    677: "Alpheratz",
    97649: "Altair",
    80763: "Antares",
    69673: "Arcturus",
    27989: "Betelgeuse",
    30438: "Canopus",
    24608: "Capella",
    36850: "Castor",
    102098: "Deneb",
    54061: "Dubhe",
    25428: "Elnath",
    113368: "Fomalhaut",
    65378: "Mizar",
    11767: "Polaris",
    37826: "Pollux",
    37279: "Procyon",
    49669: "Regulus",
    24436: "Rigel",
    85927: "Shaula",
    32349: "Sirius",
    65474: "Spica",
    91262: "Vega",
}

allstars = {
    "Achernar": 7588,
    "Acrux": 60718,
    "Adhara": 33579,
    "Agena": 68702,
    "Albireo": 95947,  # --
    "Alcor": 65477,  # --
    "Aldebaran": 21421,  # --
    "Alderamin": 105199,
    "Algenib": 15863,
    "Algieba": 50583,
    "Algol": 14576,
    "Alhena": 31681,
    "Alioth": 62956,  # --
    "Alkaid": 67301,
    "Almach": 9640,
    "Alnair": 109268,
    "Alnilam": 26311,
    "Alnitak": 26727,
    "Alphard": 46390,  # --
    "Alphecca": 76267,
    "Alpheratz": 677,  # --
    "Altair": 97649,  # --
    "Aludra": 35904,
    "Ankaa": 2081,
    "Antares": 80763,  # --
    "Arcturus": 69673,  # --
    "Arided": 102098,
    "Aridif": 102098,
    "Aspidiske": 45556,
    "Atria": 82273,
    "Avior": 41037,
    "Becrux": 62434,
    "Bellatrix": 25336,
    "Benetnash": 67301,
    "Betelgeuse": 27989,  # --
    "Birdun": 66657,
    "Canopus": 30438,  # --
    "Capella": 24608,  # --
    "Caph": 746,
    "Castor": 36850,  # --
    "Deneb": 102098,  # --
    "Deneb Kaitos": 3419,
    "Denebola": 57632,
    "Diphda": 3419,
    "Dschubba": 78401,
    "Dubhe": 54061,  # --
    "Durre Menthor": 8102,
    "Elnath": 25428,  # --
    "Enif": 107315,
    "Etamin": 87833,
    "Fomalhaut": 113368,  # --
    "Foramen": 93308,
    "Gacrux": 61084,
    "Gemma": 76267,
    "Gienah": 102488,
    "Girtab": 86228,
    "Gruid": 112122,
    "Hadar": 68702,
    "Hamal": 9884,
    "Herschel's Garnet Star": 107259,
    "Izar": 72105,
    "Kaus Australis": 90185,
    "Kochab": 72607,
    "Koo She": 42913,
    "Marchab": 113963,
    "Marfikent": 71352,
    "Markab": 45941,
    "Megrez": 59774,
    "Men": 71860,
    "Menkalinan": 28360,
    "Menkent": 68933,
    "Merak": 53910,
    "Miaplacidus": 45238,
    "Mimosa": 62434,
    "Mintaka": 25930,
    "Mira": 10826,
    "Mirach": 5447,
    "Mirfak": 15863,
    "Mirzam": 30324,
    "Mizar": 65378,  # --
    "Muhlifein": 61932,
    "Murzim": 30324,
    "Naos": 39429,
    "Nunki": 92855,
    "Peacock": 100751,
    "Phad": 58001,
    "Phecda": 58001,
    "Polaris": 11767,  # --
    "Pollux": 37826,  # --
    "Procyon": 37279,  # --
    "Ras Alhague": 86032,
    "Rasalhague": 86032,
    "Regor": 39953,
    "Regulus": 49669,  # --
    "Rigel": 24436,  # --
    "Rigel Kent": 71683,
    "Rigil Kentaurus": 71683,
    "Sabik": 84012,
    "Sadira": 16537,
    "Sadr": 100453,
    "Saiph": 27366,
    "Sargas": 86228,
    "Scheat": 113881,
    "Schedar": 3179,
    "Scutulum": 45556,
    "Shaula": 85927,  # --
    "Sirius": 32349,  # --
    "Sirrah": 677,
    "South Star": 104382,
    "Spica": 65474,  # --
    "Suhail": 44816,
    "Thuban": 68756,
    "Toliman": 71683,
    "Tseen She": 93308,
    "Tsih": 4427,
    "Turais": 45556,
    "Vega": 91262,  # --
    "Wei": 82396,
    "Wezen": 34444,
}


def get_star_data():
    with load.open(hipparcos.URL) as f:
        stardata = hipparcos.load_dataframe(f)
    return stardata
