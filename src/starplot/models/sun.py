from dataclasses import dataclass
from datetime import datetime

import numpy as np
from shapely import Polygon
from skyfield.api import Angle

from starplot.data import load
from starplot.models.base import SkyObject
from starplot.models.observer import Observer
from starplot.geometry import circle


@dataclass(slots=True)
class Sun(SkyObject):
    """Sun model."""

    name: str = "Sun"
    """Name of the Sun"""

    dt: datetime = None
    """Date/time of Sun's position"""

    apparent_size: float = 0
    """Apparent diameter (degrees)"""

    geometry: Polygon = None
    """Shapely Polygon of the Sun's extent. Right ascension coordinates are in degrees (0...360)."""

    @classmethod
    def get(
        cls,
        observer: Observer = None,
        ephemeris: str = "de421.bsp",
    ) -> "Sun":
        """
        Get the Sun for a specific date/time and observing location.

        Args:
            observer: Observer instance that specifies a time and location
            ephemeris: Ephemeris to use for calculating Sun/moon/planet positions (see [Skyfield's documentation](https://rhodesmill.org/skyfield/planets.html) for details)
        """
        RADIUS_KM = 695_700

        observer = observer or Observer(lat=None, lon=None)
        eph = load(ephemeris)
        sun = eph["sun"]

        ra, dec, distance = observer.locate(sun, ephemeris=ephemeris)

        apparent_diameter_degrees = Angle(
            radians=np.arcsin(RADIUS_KM / distance.km) * 2.0
        ).degrees

        return Sun(
            ra=ra.hours * 15,
            dec=dec.degrees,
            name="Sun",
            dt=observer.dt,
            apparent_size=apparent_diameter_degrees,
            geometry=circle((ra.hours * 15, dec.degrees), apparent_diameter_degrees),
        )
