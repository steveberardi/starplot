from datetime import datetime, timedelta
from enum import Enum

import numpy as np
from skyfield.api import Angle, wgs84
from skyfield import almanac

from starplot.data import load
from starplot.models.base import SkyObject, ShapelyPolygon
from starplot.geometry import circle
from starplot.utils import dt_or_now


class MoonPhase(str, Enum):
    """Phases of Earth's moon"""

    NEW_MOON = "New Moon"
    WAXING_CRESCENT = "Waxing Crescent"
    FIRST_QUARTER = "First Quarter"
    WAXING_GIBBOUS = "Waxing Gibbous"
    FULL_MOON = "Full Moon"
    WANING_GIBBOUS = "Waning Gibbous"
    LAST_QUARTER = "Last Quarter"
    WANING_CRESCENT = "Waning Crescent"


class Moon(SkyObject):
    """Moon model. Only used for Earth's moon right now, but will potentially represent other planets' moons in future versions."""

    name: str = "Moon"
    """Name of the moon"""

    dt: datetime
    """Date/time of moon's position"""

    apparent_size: float
    """Apparent size in the sky (degrees)"""

    phase_angle: float
    """Angle of the moon from the Sun (degrees)"""

    phase_description: str
    """Description of the moon's phase. The Moon will be considered New/Full/Quarter if it's within 12 hours of that precise phase."""

    illumination: float
    """Percent of illumination (0 to 1)"""

    geometry: ShapelyPolygon = None
    """Shapely Polygon of the moon's extent. Right ascension coordinates are in degrees (0 to 360)."""

    @classmethod
    def get(
        cls,
        dt: datetime = None,
        lat: float = None,
        lon: float = None,
        ephemeris: str = "de421_2001.bsp",
    ) -> "Moon":
        """
        Get the Moon for a specific date/time and observing location.

        Args:
            dt: Datetime you want the moon for (must be timezone aware!). _Defaults to current UTC time_.
            lat: Latitude of observing location. If you set this (and longitude), then the Moon's _apparent_ RA/DEC will be calculated.
            lon: Longitude of observing location
            ephemeris: Ephemeris to use for calculating moon positions (see [Skyfield's documentation](https://rhodesmill.org/skyfield/planets.html) for details)
        """
        RADIUS_KM = 1_740

        dt = dt_or_now(dt)
        ephemeris = load(ephemeris)
        timescale = load.timescale().from_datetime(dt)
        earth, moon = ephemeris["earth"], ephemeris["moon"]

        if lat is not None and lon is not None:
            position = earth + wgs84.latlon(lat, lon)
            astrometric = position.at(timescale).observe(moon)
            apparent = astrometric.apparent()
            ra, dec, distance = apparent.radec()
        else:
            astrometric = earth.at(timescale).observe(moon)
            ra, dec, distance = astrometric.radec()

        apparent_diameter_degrees = Angle(
            radians=np.arcsin(RADIUS_KM / distance.km) * 2.0
        ).degrees

        phase_angle = almanac.moon_phase(ephemeris, timescale).degrees

        if phase_angle <= 180:
            illumination = phase_angle / 180
        else:
            illumination = 2 - (phase_angle / 180)

        # phase angle 12 hours BEFORE dt
        phase_angle_0 = almanac.moon_phase(
            ephemeris, timescale - timedelta(hours=12)
        ).degrees

        # phase angle 12 hours AFTER dt
        phase_angle_1 = almanac.moon_phase(
            ephemeris, timescale + timedelta(hours=12)
        ).degrees

        phase = None

        if phase_angle_1 < phase_angle_0:
            phase = MoonPhase.NEW_MOON

        elif phase_angle_0 < 90 < phase_angle_1:
            phase = MoonPhase.FIRST_QUARTER

        elif phase_angle_0 < 180 < phase_angle_1:
            phase = MoonPhase.FULL_MOON

        elif phase_angle_0 < 270 < phase_angle_1:
            phase = MoonPhase.LAST_QUARTER

        elif 0 < phase_angle < 90:
            phase = MoonPhase.WAXING_CRESCENT

        elif 90 < phase_angle < 180:
            phase = MoonPhase.WAXING_GIBBOUS

        elif 180 < phase_angle < 270:
            phase = MoonPhase.WANING_GIBBOUS

        elif 270 < phase_angle < 360:
            phase = MoonPhase.WANING_CRESCENT

        return Moon(
            ra=ra.hours * 15,
            dec=dec.degrees,
            name="Moon",
            dt=dt,
            apparent_size=apparent_diameter_degrees,
            phase_angle=phase_angle,
            phase_description=phase.value,
            illumination=illumination,
            geometry=circle((ra.hours * 15, dec.degrees), apparent_diameter_degrees),
        )
