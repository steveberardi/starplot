from datetime import datetime, timedelta
from typing import Iterator
from functools import cache
from dataclasses import dataclass, fields

from skyfield.api import wgs84
from skyfield.data import mpc
from skyfield.constants import GM_SUN_Pitjeva_2005_km3_s2 as GM_SUN
from shapely import Point

from starplot.data import load
from starplot.models.base import SkyObject
from starplot.utils import dt_or_now


@dataclass
class SkyfieldComet:
    designation: str
    reference: str

    perihelion_year: int
    perihelion_month: int
    perihelion_day: float
    perihelion_distance_au: float
    eccentricity: float
    argument_of_perihelion_degrees: float
    longitude_of_ascending_node_degrees: float
    inclination_degrees: float

    perturbed_epoch_year: int | None = None
    perturbed_epoch_month: int | None = None
    perturbed_epoch_day: int | None = None

    number: int | None = None
    designation_packed: str | None = None
    orbit_type: str | None = None
    magnitude_g: float | None = None
    magnitude_k: float | None = None

    # Skyfield columns
    # ('number', (0, 4)),
    # ('orbit_type', (4, 5)),
    # ('designation_packed', (5, 12)),
    # ('perihelion_year', (14, 18)),
    # ('perihelion_month', (19, 21)),
    # ('perihelion_day', (22, 29)),
    # ('perihelion_distance_au', (30, 39)),
    # ('eccentricity', (41, 49)),
    # ('argument_of_perihelion_degrees', (51, 59)),
    # ('longitude_of_ascending_node_degrees', (61, 69)),
    # ('inclination_degrees', (71, 79)),
    # ('perturbed_epoch_year', (81, 85)),
    # ('perturbed_epoch_month', (85, 87)),
    # ('perturbed_epoch_day', (87, 89)),
    # ('magnitude_g', (91, 95)),
    # ('magnitude_k', (96, 100)),
    # ('designation', (102, 158)),
    # ('reference', (159, 168)),

    """
    MPC JSON
    {
        "Comet_num": 483,
        "Orbit_type": "P",
        "Year_of_perihelion": 2027,
        "Month_of_perihelion": 11,
        "Day_of_perihelion": 11.7324,
        "Perihelion_dist": 2.486784,
        "e": 0.221733,
        "Peri": 49.461,
        "Node": 199.0602,
        "i": 14.1756,
        "Epoch_year": 2025,
        "Epoch_month": 10,
        "Epoch_day": 22,
        "H": 17.0,
        "G": 4.0,
        "Designation_and_name": "483P-B/PANSTARRS",
        "Ref": "MPC185666"
    }
    """

    @classmethod
    def from_mpc_json(cls, data: dict) -> "SkyfieldComet":
        """Converts an MPC orbit JSON for a comet to a dataclass that Skyfield can work with"""

        d = {k.lower(): v for k, v in data.items()}

        return SkyfieldComet(
            number=d.get("comet_num"),
            orbit_type=d.get("orbit_type"),
            designation_packed=d.get("provisional_packed_desig"),
            perihelion_year=d.get("year_of_perihelion"),
            perihelion_month=d.get("month_of_perihelion"),
            perihelion_day=d.get("day_of_perihelion"),
            perihelion_distance_au=d.get("perihelion_dist"),
            eccentricity=d.get("e"),
            argument_of_perihelion_degrees=d.get("peri"),
            longitude_of_ascending_node_degrees=d.get("node"),
            inclination_degrees=d.get("i"),
            perturbed_epoch_year=d.get("epoch_year"),
            perturbed_epoch_month=d.get("epoch_month"),
            perturbed_epoch_day=d.get("epoch_day"),
            magnitude_g=d.get("g"),
            # magnitude_k=None, # no mapping?
            designation=d.get("designation_and_name"),
            reference=d.get("ref"),
        )

    @classmethod
    def from_mpc_remote(cls, name: str, reload: bool) -> "SkyfieldComet":
        """
        Create a Skyfield comet by downloading the latest MPC comet data and finding the comet by name/designation

        Args:
            name: Name/designation of the comet
            reload: If True, then the MPC data will be re-downloaded before finding the comet
        """
        comets = get_comets(reload)
        row = comets.loc[name]
        return SkyfieldComet(**row.to_dict())

    def __getitem__(self, key):
        """Allows accessing dataclass fields using dictionary-like syntax."""
        if key in [f.name for f in fields(self)]:
            return getattr(self, key)
        else:
            raise KeyError


@dataclass(slots=True, kw_only=True)
class Comet(SkyObject):
    """
    Comets can be created in three ways:

    1. [`get`][starplot.Comet.get] (designation/name)
    2. [`all`][starplot.Comet.all] (iterate through all comets available from MPC)
    3. [`from_json`][starplot.Comet.from_json] (IAU MPC JSON)

    """

    name: str = None
    """
    Name of the comet (as designated by IAU Minor Planet Center)
    """

    dt: datetime = None
    """Date/time of comet's position"""

    lat: float | None = None
    """Latitude of observing location"""

    lon: float | None = None
    """Longitude of observing location"""

    distance: float | None = None
    """Distance to comet, in Astronomical units (the Earth-Sun distance of 149,597,870,700 m)"""

    ephemeris: str = None
    """Ephemeris used when retrieving this instance"""

    geometry: Point = None
    """Shapely Point of the comet's position. Right ascension coordinates are in degrees (0...360)."""

    data: SkyfieldComet = None

    @classmethod
    def from_json(
        cls,
        data: dict,
        dt: datetime = None,
        lat: float = None,
        lon: float = None,
        ephemeris: str = "de421.bsp",
    ) -> "Comet":
        """
        Get a comet for a specific date/time/location from an IAU MPC JSON.

        Args:
            data: Dictionary of the IAU MPC JSON
            dt: Datetime you want the comet for (must be timezone aware!). _Defaults to current UTC time_.
            lat: Latitude of observing location. If you set this (and longitude), then the comet's _apparent_ RA/DEC will be calculated.
            lon: Longitude of observing location
            ephemeris: Ephemeris to use for calculating comet positions (see [Skyfield's documentation](https://rhodesmill.org/skyfield/planets.html) for details)
        """
        dt = dt_or_now(dt)
        comet = SkyfieldComet.from_mpc_json(data)

        return get_comet_at_date_location(comet, dt, lat, lon, ephemeris)

    @classmethod
    def all(
        cls,
        dt: datetime = None,
        lat: float = None,
        lon: float = None,
        ephemeris: str = "de421.bsp",
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
        comets = get_comets(reload=reload)
        for name in comets.index.values:
            row = comets.loc[name]
            comet = SkyfieldComet(**row.to_dict())
            yield get_comet_at_date_location(
                comet=comet,
                dt=dt,
                lat=lat,
                lon=lon,
                ephemeris=ephemeris,
            )

    @classmethod
    def get(
        cls,
        name: str,
        dt: datetime = None,
        lat: float = None,
        lon: float = None,
        ephemeris: str = "de421.bsp",
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
        comet = SkyfieldComet.from_mpc_remote(name, reload)
        return get_comet_at_date_location(comet, dt, lat, lon, ephemeris)

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
                comet=self.data,
                dt=dt,
                lat=self.lat,
                lon=self.lon,
                ephemeris=self.ephemeris,
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
    comet: SkyfieldComet, dt: datetime, lat: float, lon: float, ephemeris: str
) -> Comet:
    """
    Creates a Comet instance for date and (optional) observing location.
    """
    ts = load.timescale()
    eph = load(ephemeris)
    sun, earth = eph["sun"], eph["earth"]
    c = sun + mpc.comet_orbit(comet, ts, GM_SUN)
    t = ts.from_datetime(dt)

    if lat is not None and lon is not None:
        position = earth + wgs84.latlon(lat, lon)
        astrometric = position.at(t).observe(c)
        apparent = astrometric.apparent()
        ra, dec, distance = apparent.radec()
    else:
        ra, dec, distance = earth.at(t).observe(c).radec()

    return Comet(
        name=comet.designation,
        ra=ra.hours * 15,
        dec=dec.degrees,
        dt=dt,
        lat=lat,
        lon=lon,
        distance=distance.au,
        ephemeris=ephemeris,
        geometry=Point(ra.hours * 15, dec.degrees),
        data=comet,
    )
