from datetime import datetime, timezone

from pydantic import BaseModel, AwareDatetime, Field


class Observer(BaseModel):
    """Represents an observer at a specific time and place."""

    dt: AwareDatetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    """Date and time of observation (must be timezone-aware)"""

    lat: float = Field(default=0, ge=-90, le=90)
    """Latitude of observer location"""

    lon: float = Field(default=0, ge=-180, le=180)
    """Longitude of observer location"""
