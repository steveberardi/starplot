from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import pytest

from starplot import Moon, Observer, Planet, Sun


class TestMoon:
    def test_moon_get(self):
        dt = datetime(2023, 8, 27, 23, 0, 0, 0, tzinfo=timezone.utc)
        observer = Observer(
            dt=dt,
            lat=None,
            lon=None,
        )
        m = Moon.get(observer)
        assert m.ra == pytest.approx(292.53617734161276)
        assert m.dec == pytest.approx(-26.96492167310071)
        assert m.dt == dt
        assert m.apparent_size == 0.5480758923848209
        assert m.phase_description == "Waxing Gibbous"
        assert m.phase_angle == pytest.approx(135.9701133085137)
        assert m.illumination == pytest.approx(0.7553895183806317)

    def test_moon_get_new_moon(self):
        dt = datetime(2024, 4, 8, 12, 0, 0, 0, tzinfo=timezone.utc)
        observer = Observer(
            dt=dt,
            lat=None,
            lon=None,
        )
        m = Moon.get(observer)
        assert m.phase_description == "New Moon"
        assert m.phase_angle == 356.2894192723546
        assert m.illumination == 0.020614337375807645

    def test_moon_get_full_moon(self):
        dt = datetime(2024, 4, 23, 14, 0, 0, 0, tzinfo=timezone.utc)
        observer = Observer(
            dt=dt,
            lat=None,
            lon=None,
        )
        m = Moon.get(observer)
        assert m.phase_description == "Full Moon"
        assert m.phase_angle == 175.42641200608864
        assert m.illumination == 0.9745911778116035


class TestSolarEclipse:
    def test_total_solar_eclipse(self):
        # time of total eclipse in Cleveland, Ohio
        eastern = ZoneInfo("US/Eastern")
        dt = datetime(2024, 4, 8, 15, 13, 47, 0, tzinfo=eastern)
        lat = 41.482222
        lon = -81.669722

        observer = Observer(
            dt=dt,
            lat=lat,
            lon=lon,
        )
        m = Moon.get(observer)
        s = Sun.get(observer)

        assert m.ra == pytest.approx(17.616677574315425)
        assert m.dec == pytest.approx(7.471714505620887)
        assert m.apparent_size == pytest.approx(0.5615855003639567)

        assert s.ra == pytest.approx(17.629489939869988)
        assert s.dec == pytest.approx(7.477981411072887)
        assert s.apparent_size == pytest.approx(0.5321154425811137)


class TestPlanet:
    def test_planet_get(self):
        dt = datetime(2024, 4, 7, 21, 0, 0, 0, tzinfo=timezone.utc)
        observer = Observer(
            dt=dt,
            lat=None,
            lon=None,
        )
        jupiter = Planet.get("jupiter", observer)
        assert jupiter.ra == pytest.approx(46.29005575002272)
        assert jupiter.dec == pytest.approx(16.56207889273591)
        assert jupiter.dt == dt
        assert jupiter.apparent_size == 0.009162890626143375

    def test_planet_all(self):
        dt = datetime(2024, 4, 7, 21, 0, 0, 0, tzinfo=timezone.utc)
        observer = Observer(
            dt=dt,
            lat=None,
            lon=None,
        )
        planets = [p for p in Planet.all(observer)]
        assert len(planets) == 8
