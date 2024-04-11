from datetime import datetime

import numpy as np
from skyfield.api import Angle

from starplot.data import load
from starplot.models.base import SkyObject, SkyObjectManager
from starplot.utils import dt_or_now


class MoonManager(SkyObjectManager):
    @classmethod
    def all(cls):
        raise NotImplementedError

    @classmethod
    def find(cls):
        raise NotImplementedError

    @classmethod
    def get(cls, dt: datetime = None, ephemeris: str = "de421_2001.bsp"):
        RADIUS_KM = 1_740

        dt = dt_or_now(dt)
        ephemeris = load(ephemeris)
        timescale = load.timescale().from_datetime(dt)
        earth, moon = ephemeris["earth"], ephemeris["moon"]
        astrometric = earth.at(timescale).observe(moon)
        ra, dec, distance = astrometric.radec()

        apparent_diameter_degrees = Angle(
            radians=np.arcsin(RADIUS_KM / distance.km) * 2.0
        ).degrees

        return Moon(
            ra=ra.hours,
            dec=dec.degrees,
            name="Moon",
            apparent_size=apparent_diameter_degrees,
        )


class Moon(SkyObject):
    """Moon model. Only used for Earth's moon right now, but will potentially represent other planets' moons in future versions."""

    _manager = MoonManager

    name: str = "Moon"
    """Name of the moon"""

    apparent_size: float
    """Apparent size (degrees)"""

    phase: int
    """Degrees of illumination"""

    phase_descriptions: str
    """
    Description of moon phase
    * 0 degrees -- New Moon
    * 1-89 degrees -- Waxing Crescent
    * 90 degrees -- First Quarter
    * 91-179 degrees -- Waxing Gibbous
    * 180 degrees -- Full Moon
    * 181-269 degrees -- Waning Gibbous
    * 270 degrees -- Last Quarter
    * 271-259 degrees -- Waning Crescent
    """

    def __init__(self, ra: float, dec: float, name: str, apparent_size: float) -> None:
        super().__init__(ra, dec)
        self.name = name
        self.apparent_size = apparent_size

    @classmethod
    def get(dt: datetime = None, ephemeris: str = "de421_2001.bsp") -> "Moon":
        """
        Get the Moon for a specific date/time.

        Args:
            dt: Datetime you want the moon for (must be timezone aware!). _Defaults to current UTC time_.
            ephemeris: Ephemeris to use for calculating moon positions (see [Skyfield's documentation](https://rhodesmill.org/skyfield/planets.html) for details)
        """
        pass
