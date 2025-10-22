from datetime import datetime, timedelta
from typing import Iterator
from functools import cache


from skyfield.api import wgs84
from skyfield.data import mpc
from skyfield.constants import GM_SUN_Pitjeva_2005_km3_s2 as GM_SUN

from starplot.data import load
from starplot.models.base import SkyObject, ShapelyPoint
from starplot.utils import dt_or_now


class Comet(SkyObject):
    """Comet model."""

    name: str
    """
    Name of the comet (as designated by IAU Minor Planet Center)
    """

    dt: datetime
    """Date/time of comet's position"""

    lat: float | None = None
    """Latitude of observing location"""

    lon: float | None = None
    """Longitude of observing location"""

    distance: float | None = None
    """Distance to comet, in Astronomical units (the Earth-Sun distance of 149,597,870,700 m)"""

    ephemeris: str = None
    """Ephemeris used when retrieving this instance"""

    geometry: ShapelyPoint = None
    """Shapely Point of the comet's position. Right ascension coordinates are in degrees (0...360)."""

    @classmethod
    def all(
        cls,
        dt: datetime = None,
        lat: float = None,
        lon: float = None,
        ephemeris: str = "de421_2001.bsp",
        reload: bool = False,
    ) -> Iterator["Comet"]:
        """
        Iterator for getting all comets at a specific date/time and observing location.

        Args:
            dt: Datetime you want the comets for (must be timezone aware!). _Defaults to current UTC time_.
            lat: Latitude of observing location. If you set this (and longitude), then the comet's _apparent_ RA/DEC will be calculated.
            lon: Longitude of observing location
            ephemeris: Ephemeris to use for calculating comet positions (see [Skyfield's documentation](https://rhodesmill.org/skyfield/planets.html) for details)
            reload: If True, then the comet data file will be re-downloaded. Otherwise, it'll use the existing file if available.
        """
        dt = dt_or_now(dt)
        comets = get_comets()
        for name in comets.index.values:
            yield get_comet_at_date_location(
                name=name,
                dt=dt,
                lat=lat,
                lon=lon,
                ephemeris=ephemeris,
                reload=reload,
            )

    @classmethod
    def get(
        cls,
        name: str,
        dt: datetime = None,
        lat: float = None,
        lon: float = None,
        ephemeris: str = "de421_2001.bsp",
        reload: bool = False,
    ) -> "Comet":
        """
        Get a comet for a specific date/time.

        Args:
            name: Name of the comet you want to get (as designated by IAU Minor Planet Center)
            dt: Datetime you want the comet for (must be timezone aware!). _Defaults to current UTC time_.
            lat: Latitude of observing location. If you set this (and longitude), then the comet's _apparent_ RA/DEC will be calculated.
            lon: Longitude of observing location
            ephemeris: Ephemeris to use for calculating comet positions (see [Skyfield's documentation](https://rhodesmill.org/skyfield/planets.html) for details)
            reload: If True, then the comet data file will be re-downloaded. Otherwise, it'll use the existing file if available.
        """
        dt = dt_or_now(dt)
        return get_comet_at_date_location(name, dt, lat, lon, ephemeris, reload)

    def trajectory(
        self, date_start: datetime, date_end: datetime, step: timedelta = None
    ) -> Iterator["Comet"]:
        """
        Iterator for getting a trajectory of the comet.

        Args:
            date_start: Starting date/time for the trajectory (inclusive)
            date_end: End date/time for the trajectory (exclusive)
            step: Time-step for the trajectory. Defaults to 1-day

        Returns:
            Iterator that yields a Comet instance at each step in the date range
        """

        step = step or timedelta(days=1)
        dt = date_start

        while dt < date_end:
            yield get_comet_at_date_location(
                name=self.name,
                dt=dt,
                lat=self.lat,
                lon=self.lon,
                ephemeris=self.ephemeris,
                reload=False,
            )
            dt += step


@cache
def get_comets(reload=False):
    """
    Gets ALL comets currently tracked by IAU Minor Planet Center.

    Args:
        reload: If True, then redownload the comet data if it already exists

    Returns:
        DataFrame of all comets, indexed by name
    """

    with load.open(mpc.COMET_URL, reload=reload) as f:
        comets = mpc.load_comets_dataframe(f)

    # Keep only the most recent orbit for each comet, and index by designation for fast lookup.
    comets = (
        comets.sort_values("reference")
        .groupby("designation", as_index=False)
        .last()
        .set_index("designation", drop=False)
    )

    return comets


def get_comet_at_date_location(
    name: str, dt: datetime, lat: float, lon: float, ephemeris: str, reload: bool
) -> Comet:
    comets = get_comets(reload)
    row = comets.loc[name]
    ts = load.timescale()
    eph = load(ephemeris)
    sun, earth = eph["sun"], eph["earth"]
    comet = sun + mpc.comet_orbit(row, ts, GM_SUN)
    t = ts.from_datetime(dt)

    if lat is not None and lon is not None:
        position = earth + wgs84.latlon(lat, lon)
        astrometric = position.at(t).observe(comet)
        apparent = astrometric.apparent()
        ra, dec, distance = apparent.radec()
    else:
        ra, dec, distance = earth.at(t).observe(comet).radec()

    return Comet(
        name=name,
        ra=ra.hours * 15,
        dec=dec.degrees,
        dt=dt,
        lat=lat,
        lon=lon,
        distance=distance.au,
        ephemeris=ephemeris,
        geometry=ShapelyPoint(ra.hours * 15, dec.degrees),
    )
