from enum import Enum

import numpy as np

from skyfield.api import Angle

from starplot.data import load


class Planets(str, Enum):
    MERCURY = "mercury"
    VENUS = "venus"
    MARS = "mars"
    JUPITER = "jupiter"
    SATURN = "saturn"
    URANUS = "uranus"
    NEPTUNE = "neptune"


PLANET_SIZE_KM = {
    Planets.MERCURY: 2_440,
    Planets.VENUS: 6_052,
    Planets.MARS: 3_390,
    Planets.JUPITER: 69_911,
    Planets.SATURN: 58_232,
    Planets.URANUS: 25_362,
    Planets.NEPTUNE: 24_622,
}
"""
Planet sizes from NASA:

https://science.nasa.gov/resource/solar-system-sizes/

Retrieved on 28-Jan-2024
"""


def get_planet_positions(timescale, ephemeris: str = "de421_2001.bsp") -> dict:
    result = {}

    eph = load(ephemeris)
    earth = eph["earth"]

    for p in Planets:
        planet = eph[f"{p.value} barycenter"]
        astrometric = earth.at(timescale).observe(planet)
        ra, dec, distance = astrometric.radec()

        # angular diameter:
        # https://rhodesmill.org/skyfield/examples.html#what-is-the-angular-diameter-of-a-planet-given-its-radius
        radius_km = PLANET_SIZE_KM[p]
        apparent_diameter_degrees = Angle(
            radians=np.arcsin(radius_km / distance.km) * 2.0
        ).degrees

        result[p.value] = (ra.hours, dec.degrees, apparent_diameter_degrees)

    return result
