from datetime import datetime, timezone
from functools import cached_property

from pydantic import BaseModel, AwareDatetime, Field, computed_field
from skyfield.timelib import Timescale

from starplot.data import load


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

    lat: float = Field(default=0, ge=-90, le=90)
    """Latitude of observer location"""

    lon: float = Field(default=0, ge=-180, le=180)
    """Longitude of observer location"""

    class Config:
        arbitrary_types_allowed = True

    @computed_field
    @cached_property
    def timescale(self) -> Timescale:
        """
        **Read-only Property**

        Timescale instance of the specified datetime (used by Skyfield)
        """
        return load.timescale().from_datetime(self.dt)

    @computed_field
    @cached_property
    def lst(self) -> float:
        """
        **Read-only Property**

        Local sidereal time (in degrees)
        """
        return float(360.0 * self.timescale.gmst / 24.0 + self.lon) % 360.0

    # @computed_field
    # @cached_property
    # def location(self):
    #     earth = self.ephemeris["earth"]
    #     return earth + wgs84.latlon(self.lat, self.lon)

    # def observe(self):
    #     earth = self.ephemeris["earth"]
    #     self.location = earth + wgs84.latlon(self.lat, self.lon)
    #     return self.location.at(self.timescale).observe
