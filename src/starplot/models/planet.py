from datetime import datetime
from enum import Enum
from typing import Iterator

import numpy as np

from skyfield.api import Angle

from starplot.data import load
from starplot.models.base import SkyObject, SkyObjectManager
from starplot.utils import dt_or_now


class PlanetName(str, Enum):
    """Planet names"""

    MERCURY = "mercury"
    VENUS = "venus"
    MARS = "mars"
    JUPITER = "jupiter"
    SATURN = "saturn"
    URANUS = "uranus"
    NEPTUNE = "neptune"
    PLUTO = "pluto"


PLANET_LABELS_DEFAULT = {p: p.value.upper() for p in PlanetName}

PLANET_RADIUS_KM = {
    PlanetName.MERCURY: 2_440,
    PlanetName.VENUS: 6_052,
    PlanetName.MARS: 3_390,
    PlanetName.JUPITER: 69_911,
    PlanetName.SATURN: 58_232,
    PlanetName.URANUS: 25_362,
    PlanetName.NEPTUNE: 24_622,
    PlanetName.PLUTO: 1_151,
}
"""
Planet radii in kilometers, via NASA:

- https://science.nasa.gov/resource/solar-system-sizes/
- https://science.nasa.gov/dwarf-planets/pluto/facts/

Retrieved on 18-APR-2024
"""


class PlanetManager(SkyObjectManager):
    @classmethod
    def all(cls, dt: datetime = None, ephemeris: str = "de421_2001.bsp"):
        dt = dt_or_now(dt)
        ephemeris = load(ephemeris)
        timescale = load.timescale().from_datetime(dt)
        earth = ephemeris["earth"]

        for p in PlanetName:
            planet = ephemeris[f"{p.value} barycenter"]
            astrometric = earth.at(timescale).observe(planet)
            ra, dec, distance = astrometric.radec()

            # angular diameter:
            # https://rhodesmill.org/skyfield/examples.html#what-is-the-angular-diameter-of-a-planet-given-its-radius
            apparent_diameter_degrees = Angle(
                radians=np.arcsin(PLANET_RADIUS_KM[p] / distance.km) * 2.0
            ).degrees

            yield Planet(
                ra=ra.hours,
                dec=dec.degrees,
                name=p,
                dt=dt,
                apparent_size=apparent_diameter_degrees,
            )

    @classmethod
    def find(cls):
        raise NotImplementedError

    @classmethod
    def get(cls, name: str, dt: datetime = None, ephemeris: str = "de421_2001.bsp"):
        dt = dt_or_now(dt)
        for p in cls.all(dt, ephemeris):
            if p.name.lower() == name.lower():
                return p

        return None


class Planet(SkyObject):
    """Planet model."""

    _manager = PlanetManager

    name: str
    """
    Name of the planet:

    - Mercury
    - Venus
    - Mars
    - Jupiter
    - Saturn
    - Uranus
    - Neptune
    - Pluto
    
    """

    dt: datetime
    """Date/time of planet's position"""

    apparent_size: float
    """Apparent size (degrees)"""

    def __init__(
        self, ra: float, dec: float, name: str, dt: datetime, apparent_size: float
    ) -> None:
        super().__init__(ra, dec)
        self.name = name
        self.dt = dt
        self.apparent_size = apparent_size

    @classmethod
    def all(
        dt: datetime = None, ephemeris: str = "de421_2001.bsp"
    ) -> Iterator["Planet"]:
        """
        Iterator for getting all planets at a specific date/time.

        Args:
            dt: Datetime you want the planets for (must be timezone aware!). _Defaults to current UTC time_.
            ephemeris: Ephemeris to use for calculating planet positions (see [Skyfield's documentation](https://rhodesmill.org/skyfield/planets.html) for details)
        """
        pass

    @classmethod
    def get(
        name: str, dt: datetime = None, ephemeris: str = "de421_2001.bsp"
    ) -> "Planet":
        """
        Get a planet for a specific date/time.

        Args:
            name: Name of the planet you want to get (see [`Planet.name`][starplot.Planet.name] for options). Case insensitive.
            dt: Datetime you want the planet for (must be timezone aware!). _Defaults to current UTC time_.
            ephemeris: Ephemeris to use for calculating planet positions (see [Skyfield's documentation](https://rhodesmill.org/skyfield/planets.html) for details)
        """
        pass
