    "lt": {
        "legend": "legenda",
        "star magnitude": "žvaigždės ryškis",
        "star": "žvaigždė",
        "deep sky object": "tolimojo dangaus objektas",
        "open cluster": "atvirasis žvaigždžių spiečius",
        "globular cluster": "rutulinis žvaigždžių spiečius",
        "nebula": "ūkas",
        "galaxy": "galaktika",
        "dark nebula": "tamsusis ūkas",
        "association of stars": "žvaigždžių asociacija",
        "double star": "dvinarė žvaigždė",
        "emission nebula": "emisijos ūkas",
        "galaxy pair": "galaktikų pora",
        "galaxy triplet": "galaktikų tripletas",
        "galaxy cluster": "galaktikų spiečius",
        "group of galaxies": "galaktikų grupė",
        "hii ionized region": "jonizuoto vandenilio sritis (HII)",
        "nova star": "nova",
        "planetary nebula": "planetinis ūkas",
        "reflection nebula": "atspindžio ūkas",
        "star cluster nebula": "žvaigždžių spiečiaus ūkas",
        "supernova remnant": "supernovos liekana",
        "unknown": "nežinomas objektas",
        "planet": "planeta",
        "mercury": "merkurijus",
        "venus": "venera",
        "mars": "marsas",
        "jupiter": "jupiteris",
        "saturn": "saturnas",
        "uranus": "uranas",
        "neptune": "neptūnas",
        "pluto": "plutonas",
        "sun": "saulė",
        "moon": "mėnulis",
        "north": "šiaurė",
        "east": "rytai",
        "south": "pietūs",
        "west": "vakarai",
        "ecliptic": "ekliptika",
        "celestial equator": "dangaus pusiaujas",
        "n": "š",
        "e": "r",
        "s": "p",
        "w": "v",
        "milky way": "paukščių takas",
    },
}


def language_name_column(language: str, column_prefix: str = "name") -> str:
    language_name = language.replace("-", "_").lower()
    return f"{column_prefix}_{language_name}"


def translate(text: str, language: str) -> str:
    if not text:
        return text

    translation = LABELS[language.lower()].get(text.lower())

    if not translation:
        return text

    return translation.title()

