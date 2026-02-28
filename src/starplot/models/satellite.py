from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Iterator

from shapely import Point
from skyfield.api import wgs84, EarthSatellite

from starplot.data import load
from starplot.models.base import SkyObject
from starplot.models.observer import Observer

ts = load.timescale()

@dataclass(slots=True, kw_only=True)
class Satellite(SkyObject):
    """
    Satellites can be created in two ways:

    1. [`from_tle`][starplot.Satellite.from_tle] (two-line element set)
    2. [`from_json`][starplot.Satellite.from_json] (CelesTrak JSON)

    """

    name: str = None
    """Name of the satellite"""

    observer: Observer = None
    """Observer of this satellite instance"""

    distance: float | None = None
    """Distance to satellite, in Astronomical units (the Earth-Sun distance of 149,597,870,700 m)"""

    geometry: Point = None
    """Shapely Point of the satellite's position. Right ascension coordinates are in degrees (0...360)."""

    _satellite: EarthSatellite = None

    @classmethod
    def from_json(
        cls,
        data: dict,
        observer: Observer = None,
    ) -> "Satellite":
        """
        Get a satellite for a specific date/time/location from a CelesTrak JSON.

        Args:
            data: Dictionary of the CelesTrak JSON
            observer: Observer instance that specifies a time and location
        """
        observer = observer or Observer()
        return get_satellite_at_date_location(
            satellite=EarthSatellite.from_omm(ts, data), 
            observer=observer,
        )

    @classmethod
    def from_tle(
        cls,
        name: str,
        line1: str,
        line2: str,
        observer: Observer = None,
    ) -> "Satellite":
        """
        Get a satellite for a specific date/time/location from a two-line element set (TLE).

        Args:
            name: Name of the satellite
            line1: Line 1 of the two-line element set (TLE)
            line2: Line 2 of the two-line element set (TLE)
            observer: Observer instance that specifies a time and location
    
        """
        observer = observer or Observer()
        return get_satellite_at_date_location(
            satellite=EarthSatellite(
                line1,
                line2,
                name,
                ts,
            ),
            observer=observer,
        )

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
        dt = date_start
        step = step or timedelta(hours=1)

        while dt < date_end:
            observer_kwargs = self.observer.model_dump()
            observer_kwargs["dt"] = dt
            new_observer = Observer(**observer_kwargs)
            yield get_satellite_at_date_location(satellite=self._satellite, observer=new_observer)
            dt += step


def get_satellite_at_date_location(satellite: EarthSatellite, observer: Observer) -> Satellite:
    t = observer.timescale
    lat = observer.lat
    lon = observer.lon

    if lat is not None and lon is not None:
        position = wgs84.latlon(lat, lon, observer.elevation)
        difference = satellite - position
        topocentric = difference.at(t)
        ra, dec, distance = topocentric.radec()
    else:
        ra, dec, distance = satellite.at(t).radec()

    result = Satellite(
        name=satellite.name,
        ra=ra.hours * 15,
        dec=dec.degrees,
        observer=observer,
        distance=distance.au,
        geometry=Point(ra.hours * 15, dec.degrees),
    )
    setattr(result, "_satellite", satellite)
    return result
