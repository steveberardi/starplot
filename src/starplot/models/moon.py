from datetime import datetime
from enum import Enum

import numpy as np
from skyfield.api import Angle, load
from skyfield import almanac

from starplot.data import load
from starplot.models.base import SkyObject, SkyObjectManager
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
    
MOON_ILLUMINATION_PHASE_MAP = {

}

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

        ts = load.timescale()
        t = ts.utc(dt.year, dt.month, dt.day)
        phase = almanac.moon_phase(ephemeris, t).degrees
        illumination = phase/360

        # please tell me if there's a cleaner way to implement this, it killed me to write
        if phase >= 359 or phase <= 1:
            phase_description = MoonPhase.NEW_MOON
        elif 1 < phase < 89:
            phase_description = MoonPhase.WANING_CRESCENT
        elif 89 <= phase <= 91:
            phase_description = MoonPhase.FIRST_QUARTER
        elif 91 < phase < 179:
            phase_description = MoonPhase.WAXING_GIBBOUS
        elif 179 <= phase <= 181:
            phase_description = MoonPhase.FULL_MOON
        elif 181 < phase < 269:
            phase_description = MoonPhase.WANING_GIBBOUS
        elif 269 <= phase <= 271:
            phase_description = MoonPhase.LAST_QUARTER
        elif 271 < phase < 359:
            phase_description = MoonPhase.WANING_CRESCENT

        

        return Moon(
            ra=ra.hours,
            dec=dec.degrees,
            name="Moon",
            apparent_size=apparent_diameter_degrees,
            phase=phase,
            phase_description = phase_description,
            illumination = illumination,
        )


class Moon(SkyObject):
    """Moon model. Only used for Earth's moon right now, but will potentially represent other planets' moons in future versions."""

    _manager = MoonManager

    name: str = "Moon"
    """Name of the moon"""

    apparent_size: float
    """Apparent size (degrees)"""

    phase: float
    """Degrees of illumination"""

    illumination: float
    """Percentage of illumination"""

    phase_description: str
    """
    Description of moon phase
    *  degrees -- New Moon
    * 1-89 degrees -- Waxing Crescent
    * 90 degrees -- First Quarter
    * 91-179 degrees -- Waxing Gibbous
    * 180 degrees -- Full Moon
    * 181-269 degrees -- Waning Gibbous
    * 270 degrees -- Last Quarter
    * 271-259 degrees -- Waning Crescent
    """

    def __init__(self, ra: float, dec: float, name: str, apparent_size: float, phase: float, phase_description: str, illumination: str) -> None:
        super().__init__(ra, dec)
        self.name = name
        self.apparent_size = apparent_size
        self.phase = phase
        self.phase_description = phase_description
        self.illumination = illumination

    @classmethod
    def get(dt: datetime = None, ephemeris: str = "de421_2001.bsp") -> "Moon":
        """
        Get the Moon for a specific date/time.

        Args:
            dt: Datetime you want the moon for (must be timezone aware!). _Defaults to current UTC time_.
            ephemeris: Ephemeris to use for calculating moon positions (see [Skyfield's documentation](https://rhodesmill.org/skyfield/planets.html) for details)
        """
        pass
