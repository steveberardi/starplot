import numpy as np
from skyfield.api import Angle

from starplot.data import load
from starplot.models.base import SkyObject, SkyObjectManager


class SunManager(SkyObjectManager):
    @classmethod
    def all(cls):
        raise NotImplementedError

    @classmethod
    def find(cls):
        raise NotImplementedError

    @classmethod
    def get(cls, dt, ephemeris: str = "de421_2001.bsp"):
        RADIUS_KM = 695_700

        ephemeris = load(ephemeris)
        timescale = load.timescale().from_datetime(dt)
        earth, moon = ephemeris["earth"], ephemeris["sun"]
        astrometric = earth.at(timescale).observe(moon)
        ra, dec, distance = astrometric.radec()

        apparent_diameter_degrees = Angle(
            radians=np.arcsin(RADIUS_KM / distance.km) * 2.0
        ).degrees

        return Sun(
            ra=ra.hours,
            dec=dec.degrees,
            name="Sun",
            apparent_size=apparent_diameter_degrees,
        )


class Sun(SkyObject):
    """Sun model."""

    _manager = SunManager

    name: str = "Sun"
    """Name of the Sun"""

    apparent_size: float
    """Apparent size (degrees)"""

    def __init__(self, ra: float, dec: float, name: str, apparent_size: float) -> None:
        super().__init__(ra, dec)
        self.name = name
        self.apparent_size = apparent_size

    @classmethod
    def get(dt, ephemeris: str = "de421_2001.bsp"):
        """
        Get the Sun for a specific date/time.

        Args:
            dt: Datetime you want the Sun for (must be timezone aware!)
            ephemeris: Ephemeris to use for calculating Sun/moon/planet positions (see [Skyfield's documentation](https://rhodesmill.org/skyfield/planets.html) for details)
        """
        pass
