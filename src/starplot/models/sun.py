from datetime import datetime

import numpy as np
from skyfield.api import Angle, wgs84

from starplot.data import load
from starplot.models.base import SkyObject, ShapelyPolygon
from starplot.geometry import circle
from starplot.utils import dt_or_now


class Sun(SkyObject):
    """Sun model."""

    name: str = "Sun"
    """Name of the Sun"""

    dt: datetime
    """Date/time of Sun's position"""

    apparent_size: float
    """Apparent size (degrees)"""

    geometry: ShapelyPolygon = None
    """Shapely Polygon of the Sun's extent. Right ascension coordinates are in degrees (0...360)."""

    @classmethod
    def get(
        cls,
        dt: datetime = None,
        lat: float = None,
        lon: float = None,
        ephemeris: str = "de421_2001.bsp",
    ) -> "Sun":
        """
        Get the Sun for a specific date/time and observing location.

        Args:
            dt: Datetime you want the Sun for (must be timezone aware!). _Defaults to current UTC time_.
            lat: Latitude of observing location. If you set this (and longitude), then the Sun's _apparent_ RA/DEC will be calculated.
            lon: Longitude of observing location
            ephemeris: Ephemeris to use for calculating Sun/moon/planet positions (see [Skyfield's documentation](https://rhodesmill.org/skyfield/planets.html) for details)
        """
        RADIUS_KM = 695_700

        dt = dt_or_now(dt)
        ephemeris = load(ephemeris)
        timescale = load.timescale().from_datetime(dt)
        earth, sun = ephemeris["earth"], ephemeris["sun"]

        if lat is not None and lon is not None:
            position = earth + wgs84.latlon(lat, lon)
            astrometric = position.at(timescale).observe(sun)
            apparent = astrometric.apparent()
            ra, dec, distance = apparent.radec()
        else:
            astrometric = earth.at(timescale).observe(sun)
            ra, dec, distance = astrometric.radec()

        apparent_diameter_degrees = Angle(
            radians=np.arcsin(RADIUS_KM / distance.km) * 2.0
        ).degrees

        return Sun(
            ra=ra.hours * 15,
            dec=dec.degrees,
            name="Sun",
            dt=dt,
            apparent_size=apparent_diameter_degrees,
            geometry=circle((ra.hours * 15, dec.degrees), apparent_diameter_degrees),
        )
