from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Iterator

import numpy as np

from shapely import Polygon
from skyfield.api import Angle, wgs84

from starplot.data import load
from starplot.models.base import SkyObject
from starplot.models.observer import Observer
from starplot.geometry import circle
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


@dataclass(slots=True, kw_only=True)
class Planet(SkyObject):
    """Planet model."""

    name: str = None
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

    dt: datetime = None
    """Date/time of planet's position"""

    apparent_size: float = 0
    """Apparent diameter (degrees)"""

    geometry: Polygon = None
    """Shapely Polygon of the planet's extent. Right ascension coordinates are in degrees (0...360)."""

    @classmethod
    def all(
        cls,
        observer: Observer = None,
        ephemeris: str = "de421.bsp",
    ) -> Iterator["Planet"]:
        """
        Iterator for getting all planets at a specific date/time and observing location.

        Args:
            observer: Observer instance that specifies a time and location
            ephemeris: Ephemeris to use for calculating planet positions (see [Skyfield's documentation](https://rhodesmill.org/skyfield/planets.html) for details)
        """

        observer = observer or Observer(lat=None, lon=None)
        eph = load(ephemeris)
        
        for p in PlanetName:
            planet = eph[f"{p.value} barycenter"]
            ra, dec, distance = observer.locate(planet, ephemeris=ephemeris)

            # angular diameter:
            # https://rhodesmill.org/skyfield/examples.html#what-is-the-angular-diameter-of-a-planet-given-its-radius
            apparent_diameter_degrees = Angle(
                radians=np.arcsin(PLANET_RADIUS_KM[p] / distance.km) * 2.0
            ).degrees

            yield Planet(
                ra=ra.hours * 15,
                dec=dec.degrees,
                name=p,
                dt=observer.dt,
                apparent_size=apparent_diameter_degrees,
                geometry=circle(
                    (ra.hours * 15, dec.degrees), apparent_diameter_degrees
                ),
            )

    @classmethod
    def get(
        cls,
        name: str,
        observer: Observer = None,
        ephemeris: str = "de421.bsp",
    ) -> "Planet":
        """
        Get a planet for a specific date/time.

        Args:
            name: Name of the planet you want to get (see [`Planet.name`][starplot.Planet.name] for options). Case insensitive.
            observer: Observer instance that specifies a time and location
            ephemeris: Ephemeris to use for calculating planet positions (see [Skyfield's documentation](https://rhodesmill.org/skyfield/planets.html) for details)
        """
        for p in cls.all(observer, ephemeris):
            if p.name.lower() == name.lower():
                return p

        return None
