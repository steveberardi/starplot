from enum import Enum
from typing import Dict

import numpy as np

from skyfield.api import Angle


class Planet(str, Enum):
    """Planets ... Coming Soon: Pluto :)"""

    MERCURY = "mercury"
    VENUS = "venus"
    MARS = "mars"
    JUPITER = "jupiter"
    SATURN = "saturn"
    URANUS = "uranus"
    NEPTUNE = "neptune"


PLANET_LABELS_DEFAULT = {p: p.value.upper() for p in Planet}

PLANET_SIZE_KM = {
    Planet.MERCURY: 2_440,
    Planet.VENUS: 6_052,
    Planet.MARS: 3_390,
    Planet.JUPITER: 69_911,
    Planet.SATURN: 58_232,
    Planet.URANUS: 25_362,
    Planet.NEPTUNE: 24_622,
}
"""
Planet sizes from NASA:

https://science.nasa.gov/resource/solar-system-sizes/

Retrieved on 28-Jan-2024
"""


def get_planet_positions(timescale, ephemeris) -> Dict[Planet, tuple]:
    result = {}
    earth = ephemeris["earth"]

    for p in Planet:
        planet = ephemeris[f"{p.value} barycenter"]
        astrometric = earth.at(timescale).observe(planet)
        ra, dec, distance = astrometric.radec()

        # angular diameter:
        # https://rhodesmill.org/skyfield/examples.html#what-is-the-angular-diameter-of-a-planet-given-its-radius
        radius_km = PLANET_SIZE_KM[p]
        apparent_diameter_degrees = Angle(
            radians=np.arcsin(radius_km / distance.km) * 2.0
        ).degrees

        result[p] = (ra.hours, dec.degrees, apparent_diameter_degrees)

    return result
