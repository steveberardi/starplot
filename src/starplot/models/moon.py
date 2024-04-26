from datetime import datetime, timedelta
from enum import Enum

import numpy as np
from skyfield.api import Angle
from skyfield.api import load as skyload
from starplot.data import load
from skyfield import almanac

from starplot.data import load
from starplot.models.base import SkyObject, SkyObjectManager
from starplot.styles.base import MarkerSymbolEnum
from starplot.utils import dt_or_now

class MoonPhaseEnum(str, Enum):
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
    def _calc_moon_phase_day_range(cls, year: int, month: int, day: int, ephemeris: str = "de421_2001.bsp"):
        ts = skyload.timescale()
        
        # establish monthlong range to search for nearst Full Moon
        date = ts.utc(year, month, day)
        t0 = date - 15 # 15 days earlier
        t1 = date + 15 # 15 days later
        ephemeris = load(ephemeris)

        t, y = almanac.find_discrete(t0, t1, almanac.moon_phases(ephemeris))

        closestPhase = []
        
        # only include Full Moon dates (1)
        for i in range(len(y)):
            if y[i] == 1:
                closestPhase.append(t[i])
        
        while len(closestPhase) > 1:
            if abs(date-closestPhase[0]) < abs(date-closestPhase[1]):
                del closestPhase[1]
            else:
                del closestPhase[0]

        nearphase = closestPhase[0].utc
        curr_date = ts.utc(nearphase.year, nearphase.month, nearphase.day, nearphase.hour, nearphase.minute)
        comp_date = curr_date + timedelta(hours=12)

        phase_mid = almanac.moon_phase(ephemeris, curr_date).degrees
        phase_pre = almanac.moon_phase(ephemeris, comp_date).degrees


        phase_range = abs(phase_mid-phase_pre)

        return phase_range

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
        t = ts.utc(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
        phase = almanac.moon_phase(ephemeris, t).degrees
        if phase <= 180:
            illumination = phase / 180
        else:
            illumination = 2 - (phase / 180)

        day_range = cls._calc_moon_phase_day_range(dt.year, dt.month, dt.day)

        phaseMap = {
            MoonPhaseEnum.NEW_MOON: 0,
            MoonPhaseEnum.FIRST_QUARTER: 90,
            MoonPhaseEnum.FULL_MOON: 180, 
            MoonPhaseEnum.LAST_QUARTER: 270,
        }
        phase_description = None
        for desc, att in phaseMap.items():
            if abs(phase-att) < day_range:
                phase_description = desc

        if phase_description is None:
            if 0 < phase < 90:
                phase_description = MoonPhaseEnum.WANING_CRESCENT
            elif 90 < phase < 180:
                phase_description = MoonPhaseEnum.WAXING_GIBBOUS
            elif 180 < phase < 270:
                phase_description = MoonPhaseEnum.WANING_GIBBOUS
            elif 270 < phase < 360:
                phase_description = MoonPhaseEnum.WANING_CRESCENT


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
    """Description of moon phase"""

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
