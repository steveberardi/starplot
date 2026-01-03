from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Iterator

from shapely import Point
from skyfield.api import wgs84, EarthSatellite
from skyfield.timelib import Timescale

from starplot.data import load
from starplot.models.base import SkyObject
from starplot.utils import dt_or_now


@dataclass(slots=True, kw_only=True)
class Satellite(SkyObject):
    """
    Satellites can be created in two ways:

    1. [`from_tle`][starplot.Satellite.from_tle] (two-line element set)
    2. [`from_json`][starplot.Satellite.from_json] (CelesTrak JSON)

    """

    name: str = None
    """
    Name of the satellite
    """

    dt: datetime = None
    """Date/time of satellite's position"""

    lat: float | None = None
    """Latitude of observing location"""

    lon: float | None = None
    """Longitude of observing location"""

    distance: float | None = None
    """Distance to satellite, in Astronomical units (the Earth-Sun distance of 149,597,870,700 m)"""

    ephemeris: str = None
    """Ephemeris used when retrieving this instance"""

    geometry: Point = None
    """Shapely Point of the satellite's position. Right ascension coordinates are in degrees (0...360)."""

    _satellite: EarthSatellite = None

    @classmethod
    def from_json(
        cls,
        data: dict,
        dt: datetime = None,
        lat: float = None,
        lon: float = None,
        ephemeris: str = "de421.bsp",
    ) -> "Satellite":
        """
        Get a satellite for a specific date/time/location from a CelesTrak JSON.

        Args:
            data: Dictionary of the CelesTrak JSON
            dt: Datetime you want the satellite for (must be timezone aware!). _Defaults to current UTC time_.
            lat: Latitude of observing location. If you set this (and longitude), then the satellite's _apparent_ RA/DEC will be calculated.
            lon: Longitude of observing location
            ephemeris: Ephemeris to use for calculating satellite positions (see [Skyfield's documentation](https://rhodesmill.org/skyfield/planets.html) for details)
        """
        dt = dt_or_now(dt)
        ts = load.timescale()
        satellite = EarthSatellite.from_omm(ts, data)

        return get_satellite_at_date_location(satellite, dt, lat, lon, ts)

    @classmethod
    def from_tle(
        cls,
        name: str,
        line1: str,
        line2: str,
        dt: datetime = None,
        lat: float = None,
        lon: float = None,
        ephemeris: str = "de421.bsp",
    ) -> "Satellite":
        """
        Get a satellite for a specific date/time/location from a two-line element set (TLE).

        Args:
            name: Name of the satellite
            line1: Line 1 of the two-line element set (TLE)
            line2: Line 2 of the two-line element set (TLE)
            dt: Datetime you want the satellite for (must be timezone aware!). _Defaults to current UTC time_.
            lat: Latitude of observing location. If you set this (and longitude), then the satellite's _apparent_ RA/DEC will be calculated.
            lon: Longitude of observing location
            ephemeris: Ephemeris to use for calculating satellite positions (see [Skyfield's documentation](https://rhodesmill.org/skyfield/planets.html) for details)
        """
        dt = dt_or_now(dt)
        ts = load.timescale()
        satellite = EarthSatellite(
            line1,
            line2,
            name,
            ts,
        )

        return get_satellite_at_date_location(satellite, dt, lat, lon, ts)

    def trajectory(
        self, date_start: datetime, date_end: datetime, step: timedelta = None
    ) -> Iterator["Satellite"]:
        """
        Iterator for getting a trajectory of the satellite.

        Args:
            date_start: Starting date/time for the trajectory (inclusive)
            date_end: End date/time for the trajectory (exclusive)
            step: Time-step for the trajectory. Defaults to 1-day

        Returns:
            Iterator that yields a Satellite instance at each step in the date range
        """

        step = step or timedelta(hours=1)
        dt = date_start
        ts = load.timescale()

        while dt < date_end:
            yield get_satellite_at_date_location(
                self._satellite, dt, self.lat, self.lon, ts
            )
            dt += step


def get_satellite_at_date_location(
    satellite: EarthSatellite, dt: datetime, lat: float, lon: float, ts: Timescale
) -> Satellite:
    t = ts.from_datetime(dt)

    if lat is not None and lon is not None:
        position = wgs84.latlon(lat, lon)
        difference = satellite - position
        topocentric = difference.at(t)
        ra, dec, distance = topocentric.radec()
        # alt, az, distance = topocentric.altaz()
        # print(alt, az)
    else:
        ra, dec, distance = satellite.at(t).radec()

    result = Satellite(
        name=satellite.name,
        ra=ra.hours * 15,
        dec=dec.degrees,
        dt=dt,
        lat=lat,
        lon=lon,
        distance=distance.au,
        ephemeris="na",
        geometry=Point(ra.hours * 15, dec.degrees),
    )
    setattr(result, "_satellite", satellite)
    return result
