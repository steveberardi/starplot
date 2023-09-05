from enum import Enum

from starplot.data import load


class Planets(str, Enum):
    MERCURY = "mercury"
    VENUS = "venus"
    MARS = "mars"
    JUPITER = "jupiter"
    SATURN = "saturn"
    URANUS = "uranus"
    NEPTUNE = "neptune"


def get_planet_positions(timescale, ephemeris: str = "de421_2001.bsp") -> dict:
    result = {}

    eph = load(ephemeris)
    earth = eph["earth"]

    for p in Planets:
        planet = eph[f"{p.value} barycenter"]
        astrometric = earth.at(timescale).observe(planet)
        ra, dec, _ = astrometric.radec()

        result[p.value] = (ra.hours, dec.degrees)

    return result
