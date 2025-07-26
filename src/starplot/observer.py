from datetime import datetime, timezone
from functools import cached_property

from pydantic import BaseModel, AwareDatetime, Field, computed_field
from skyfield.timelib import Timescale

from starplot.data import load

class Observer(BaseModel):
    """Represents an observer at a specific time and place."""

    dt: AwareDatetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    """Date and time of observation (must be timezone-aware)"""

    lat: float = Field(default=0, ge=-90, le=90)
    """Latitude of observer location"""

    lon: float = Field(default=0, ge=-180, le=180)
    """Longitude of observer location"""

    @computed_field
    @cached_property
    def timescale(self) -> Timescale:
        return load.timescale().from_datetime(self.dt)

    @computed_field
    @cached_property
    def lst(self) -> float:
        """Local sidereal time (in degrees)"""
        return (360.0 * self.timescale.gmst / 24.0 + self.lon) % 360.0
