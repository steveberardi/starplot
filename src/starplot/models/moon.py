from datetime import datetime, timedelta
from enum import Enum

import numpy as np
from skyfield.api import Angle
from skyfield import almanac

from starplot.data import load
from starplot.models.base import SkyObject, SkyObjectManager
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


class MoonManager(SkyObjectManager):
    @classmethod
    def all(cls):
        raise NotImplementedError

    @classmethod
    def find(cls):
        raise NotImplementedError

    @classmethod
    def _calc_moon_phase_day_range(
        cls, year: int, month: int, day: int, ephemeris: str = "de421_2001.bsp"
    ):
        ts = load.timescale()

        # establish monthlong range to search for nearst Full Moon
        date = ts.utc(year, month, day)
        t0 = date - 15  # 15 days earlier
        t1 = date + 15  # 15 days later
        ephemeris = load(ephemeris)

        times_of_phases, phase_types = almanac.find_discrete(
            t0, t1, almanac.moon_phases(ephemeris)
        )

        closest_phase = []

        # only include Full Moon dates (1)
        for i in range(len(phase_types)):
            if phase_types[i] == 1:
                closest_phase.append(times_of_phases[i])

        nearphase = closest_phase[0].utc
        curr_date = ts.utc(
            nearphase.year,
            nearphase.month,
            nearphase.day,
            nearphase.hour,
            nearphase.minute,
        )
        comp_date = curr_date + timedelta(hours=12)

        phase_mid = almanac.moon_phase(ephemeris, curr_date).degrees
        phase_pre = almanac.moon_phase(ephemeris, comp_date).degrees

        phase_range = abs(phase_mid - phase_pre)

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
        phase_angle = almanac.moon_phase(ephemeris, t).degrees
        if phase_angle <= 180:
            illumination = phase_angle / 180
        else:
            illumination = 2 - (phase_angle / 180)

        day_range = cls._calc_moon_phase_day_range(dt.year, dt.month, dt.day)

        phase_map = {
            MoonPhaseEnum.NEW_MOON: 0,
            MoonPhaseEnum.FIRST_QUARTER: 90,
            MoonPhaseEnum.FULL_MOON: 180,
            MoonPhaseEnum.LAST_QUARTER: 270,
        }
        phase_description = None
        for desc, att in phase_map.items():
            if abs(phase_angle - att) < day_range:
                phase_description = desc

        if phase_angle > (360 - day_range):
            phase_description = MoonPhaseEnum.NEW_MOON

        if phase_description is None:
            if 0 < phase_angle < 90:
                phase_description = MoonPhaseEnum.WAXING_CRESCENT
            elif 90 < phase_angle < 180:
                phase_description = MoonPhaseEnum.WAXING_GIBBOUS
            elif 180 < phase_angle < 270:
                phase_description = MoonPhaseEnum.WANING_GIBBOUS
            elif 270 < phase_angle < 360:
                phase_description = MoonPhaseEnum.WANING_CRESCENT

        return Moon(
            ra=ra.hours,
            dec=dec.degrees,
            name="Moon",
            dt=dt,
            apparent_size=apparent_diameter_degrees,
            phase_angle=phase_angle,
            phase_description=phase_description,
            illumination=illumination,
        )


class Moon(SkyObject):
    """Moon model. Only used for Earth's moon right now, but will potentially represent other planets' moons in future versions."""

    _manager = MoonManager

    name: str = "Moon"
    """Name of the moon"""

    dt: datetime
    """Date/time of moon's position"""

    apparent_size: float
    """Apparent size (degrees)"""

    phase_angle: float
    """Angle of the moon from the Sun (degrees)"""

    illumination: float
    """Percent of illumination (0...1)"""

    phase_description: str
    """Description of moon phase"""

    def __init__(
        self,
        ra: float,
        dec: float,
        name: str,
        dt: datetime,
        apparent_size: float,
        phase_angle: float,
        phase_description: str,
        illumination: str,
    ) -> None:
        super().__init__(ra, dec)
        self.name = name
        self.dt = dt
        self.apparent_size = apparent_size
        self.phase_angle = phase_angle
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
