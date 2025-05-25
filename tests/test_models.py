from datetime import datetime

import pytest

from pytz import timezone

from starplot import _, DSO, Star, Constellation, Sun, Moon, Planet


class TestStar:
    def test_star_get(self):
        sirius = Star.get(name="Sirius")
        constellation = sirius.constellation()

        assert sirius.magnitude == -1.44
        assert sirius.hip == 32349
        assert sirius.constellation_id == "cma"

        assert constellation.iau_id == "cma"
        assert constellation.name == "Canis Major"

    def test_star_get_sql(self):
        vega = Star.get(sql="select * from _ where name='Vega'")

        assert vega.magnitude == 0.03
        assert vega.hip == 91262
        assert vega.constellation_id == "lyr"

    def test_star_get_raises_exception(self):
        with pytest.raises(ValueError):
            Star.get(name=None)

    def test_star_find(self):
        hipstars = Star.find(where=[_.hip.notnull()])
        assert len(hipstars) == 121_477

        names = {"Sirius", "Bellatrix", "Castor", "Vega"}
        bright = Star.find(where=[_.name.isin(names)])
        assert len(bright) == 4
        assert set([s.name for s in bright]) == names

    def test_star_find_sql(self):
        bright_stars = Star.find(sql="select * from _ where magnitude < 3")
        assert len(bright_stars) == 196

    def test_star_find_intersects(self):
        m45 = DSO.get(m="45")
        m45_stars = Star.find(
            where=[_.geometry.intersects(m45.geometry), _.magnitude < 8]
        )

        for star in m45_stars:
            assert star.geometry.intersects(m45.geometry)


class TestConstellation:
    def test_constellation_get(self):
        hercules = Constellation.get(iau_id="her")
        assert hercules.name == "Hercules"
        assert hercules.ra == 253.2
        assert hercules.dec == 34.86

        draco = Constellation.get(sql="select * from _ where iau_id='dra'")
        assert draco.name == "Draco"

    def test_constellation_find(self):
        results = Constellation.find(
            where=[_.name.isin(["Canis Major", "Andromeda", "Orion"])]
        )
        assert len(results) == 3

        sql_results = Constellation.find(sql="select * from _ where name = 'Lyra'")
        assert len(sql_results) == 1
        assert sql_results[0].iau_id == "lyr"


class TestDSO:
    def test_dso_get(self):
        m13 = DSO.get(m="13")
        assert m13.ra == 250.4235
        assert m13.dec == 36.4613
        assert m13.m == "13"
        assert m13.ngc == "6205"
        assert m13.ic is None
        assert m13.constellation_id == "her"

        m44 = DSO.get(sql="select * from _ where m='44'")
        assert m44.m == "44"
        assert m44.constellation_id == "cnc"

    def test_dso_find_messier(self):
        results = DSO.find(where=[_.m.notnull()])
        assert len(results) == 110

        sql_results = DSO.find(sql="select * from _ where m is not null")
        assert len(sql_results) == 110

    def test_dso_find_duplicate(self):
        results = DSO.find(where=[_.ngc == "5273"])
        assert len(results) == 2

        for r in results:
            assert r.m is None
            assert r.ngc == "5273"
            assert r.ic == "895"


class TestMoon:
    def test_moon_get(self):
        dt = timezone("UTC").localize(datetime(2023, 8, 27, 23, 0, 0, 0))
        m = Moon.get(dt)
        assert m.ra == 292.53617734161276
        assert m.dec == -26.96492167310071
        assert m.dt == dt
        assert m.apparent_size == 0.5480758923848209
        assert m.phase_description == "Waxing Gibbous"
        assert m.phase_angle == 135.9701133085137
        assert m.illumination == 0.7553895183806317

    def test_moon_get_new_moon(self):
        dt = timezone("UTC").localize(datetime(2024, 4, 8, 12, 0, 0, 0))
        m = Moon.get(dt)
        assert m.phase_description == "New Moon"
        assert m.phase_angle == 356.2894192723546
        assert m.illumination == 0.020614337375807645

    def test_moon_get_full_moon(self):
        dt = timezone("UTC").localize(datetime(2024, 4, 23, 14, 0, 0, 0))
        m = Moon.get(dt)
        assert m.phase_description == "Full Moon"
        assert m.phase_angle == 175.42641200608864
        assert m.illumination == 0.9745911778116035


class TestSolarEclipse:
    def test_total_solar_eclipse(self):
        # time of total eclipse in Cleveland, Ohio
        eastern = timezone("US/Eastern")
        dt = eastern.localize(datetime(2024, 4, 8, 15, 13, 47, 0))
        lat = 41.482222
        lon = -81.669722

        m = Moon.get(dt=dt, lat=lat, lon=lon)
        s = Sun.get(dt=dt, lat=lat, lon=lon)

        assert m.ra == 17.611428857038238
        assert m.dec == 7.469561912433153
        assert m.apparent_size == 0.5615855003639567

        assert s.ra == 17.624241364540502
        assert s.dec == 7.475828971935881
        assert s.apparent_size == 0.5321154425811137


class TestPlanet:
    def test_planet_get(self):
        dt = timezone("UTC").localize(datetime(2024, 4, 7, 21, 0, 0, 0))
        jupiter = Planet.get("jupiter", dt)
        assert jupiter.ra == 46.29005575002272
        assert jupiter.dec == 16.56207889273591
        assert jupiter.dt == dt
        assert jupiter.apparent_size == 0.009162890626143375

    def test_planet_all(self):
        dt = timezone("UTC").localize(datetime(2024, 4, 7, 21, 0, 0, 0))
        planets = [p for p in Planet.all(dt)]
        assert len(planets) == 8
