from datetime import datetime

import pytest

from pytz import timezone

from starplot import DSO, Star, Moon, Planet


class TestStar:
    def test_star_true_expressions(self):
        star = Star(ra=2, dec=20, magnitude=4, bv=2.12, name="fakestar")

        expressions = [
            Star.ra < 24,
            Star.dec > 5,
            Star.ra <= 2,
            Star.hip.is_null(),
            Star.name.is_in(["stuff", "sirius", "fakestar"]),
            (Star.name == "wrong") | (Star.name == "fakestar"),
            Star.name != "noname",
            (Star.name == "bellatrix")
            | ((Star.name == "fakestar") & (Star.magnitude < 5)),
        ]
        assert all([e.evaluate(star) for e in expressions])

    def test_star_false_expressions(self):
        star = Star(ra=2, dec=20, magnitude=4, bv=2.12, name="fakestar")

        expressions = [
            Star.ra > 4,
            Star.dec < 5,
            Star.hip.is_not_null(),
            Star.name.is_not_in(["stuff", "sirius", "fakestar"]),
            (Star.name == "wrong") | (Star.name != "fakestar"),
        ]
        assert not any([e.evaluate(star) for e in expressions])

    def test_star_get(self):
        sirius = Star.get(name="Sirius")

        assert sirius.magnitude == -1.44
        assert sirius.hip == 32349

    def test_star_get_raises_exception(self):
        with pytest.raises(ValueError):
            Star.get(name=None)

    def test_star_find(self):
        hipstars = Star.find(where=[Star.hip.is_not_null()])
        assert len(hipstars) == 118_218

        names = {"Sirius", "Bellatrix", "Castor", "Vega"}
        bright = Star.find(where=[Star.name.is_in(names)])
        assert len(bright) == 4
        assert set([s.name for s in bright]) == names


class TestDSO:
    def test_dso_get(self):
        m13 = DSO.get(m="13")
        assert m13.ra == 16.694897222222224
        assert m13.dec == 36.46130555555556
        assert m13.m == "13"
        assert m13.ngc == "6205"
        assert m13.ic is None

    def test_dso_find_messier(self):
        results = DSO.find(where=[DSO.m.is_not_null()])
        assert len(results) == 110

    def test_dso_find_duplicate(self):
        results = DSO.find(where=[DSO.ngc == "5273"])
        assert len(results) == 2

        for r in results:
            assert r.m is None
            assert r.ngc == "5273"
            assert r.ic == "895"


class TestMoon:
    def test_moon_get(self):
        dt = timezone("UTC").localize(datetime(2023, 8, 27, 23, 0, 0, 0))
        m = Moon.get(dt)
        assert m.ra == 19.502411822774185
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


class TestPlanet:
    def test_planet_get(self):
        dt = timezone("UTC").localize(datetime(2024, 4, 7, 21, 0, 0, 0))
        jupiter = Planet.get("jupiter", dt)
        assert jupiter.ra == 3.086003716668181
        assert jupiter.dec == 16.56207889273591
        assert jupiter.dt == dt
        assert jupiter.apparent_size == 0.009162890626143375

    def test_planet_all(self):
        dt = timezone("UTC").localize(datetime(2024, 4, 7, 21, 0, 0, 0))
        planets = [p for p in Planet.all(dt)]
        assert len(planets) == 8
