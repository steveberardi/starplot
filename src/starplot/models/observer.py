from datetime import datetime, timezone
from functools import cached_property
from typing import Callable


from pydantic import BaseModel, AwareDatetime, Field, computed_field
from skyfield.timelib import Timescale
from skyfield.api import wgs84, Star as SkyfieldStar

from starplot.data import load

ts = load.timescale()


class Observer(BaseModel):
    """
    Represents an observer at a specific time and place.

    Example:

    ```python
    obs = Observer(
        dt=datetime(2025, 10, 13, 21, 0, 0, tzinfo=ZoneInfo('US/Pacific')),
        lat=33.363484,
        lon=-116.836394,
    )
    ```

    """

    dt: AwareDatetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    """
    Date and time of observation (**must be timezone-aware**).
    
    Defaults to current time in UTC.
    """

    lat: float | None = Field(default=0, ge=-90, le=90)
    """Latitude of observer location"""

    lon: float | None = Field(default=0, ge=-180, le=180)
    """Longitude of observer location"""

    elevation: float = 0
    """Elevation of observer, in meters"""

    temperature: float | None = None
    """Temperature in degrees Celsius. This is only used for determining atmospheric refraction for apparent positions."""

    pressure: float | None = None
    """Atmospheric pressure in millibars. This is only used for determining atmospheric refraction for apparent positions."""

    class Config:
        arbitrary_types_allowed = True

    @computed_field
    @cached_property
    def timescale(self) -> Timescale:
        """
        **Read-only Property**

        Timescale instance of the specified datetime (used by Skyfield)
        """
        return ts.from_datetime(self.dt)

    @computed_field
    @cached_property
    def lst(self) -> float:
        """
        **Read-only Property**

        Local sidereal time (in degrees)
        """
        return float(360.0 * self.timescale.gmst / 24.0 + self.lon) % 360.0

    @computed_field
    @cached_property
    def has_location(self) -> bool:
        return self.lat is not None and self.lon is not None

    @classmethod
    def at_epoch(cls, epoch: float) -> "Observer":
        """
        Returns an Observer for the specified epoch (Julian year)
        """
        return Observer(dt=ts.J(epoch).utc_datetime())

    def position(self, ephemeris: str = "de421.bsp"):
        """
        Returns a Skyfield position for this observer.

        If the observer has no lat/lon, then the Earth's center will be returned.

        Args:
            ephemeris: Ephemeris to use
        """
        eph = load(ephemeris)
        earth = eph["earth"]

        if self.lat is None and self.lon is None:
            return earth

        return earth + wgs84.latlon(self.lat, self.lon, self.elevation)

    def observe(self, ephemeris: str = "de421.bsp") -> Callable:
        return self.position(ephemeris).at(self.timescale).observe

    def locate(self, obj: SkyfieldStar, ephemeris: str = "de421.bsp"):
        if self.has_location:
            ra, dec, distance = self.observe(ephemeris)(obj).apparent().radec()
            return ra, dec, distance

        ra, dec, distance = self.observe(ephemeris)(obj).radec()
        return ra, dec, distance
