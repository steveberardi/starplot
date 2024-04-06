from datetime import datetime

import pytest

from pytz import timezone

from starplot import Star, Moon


def test_star_true_expressions():
    star = Star(ra=2, dec=20, magnitude=4, bv=2.12, name="fakestar")

    expressions = [
        Star.ra < 24,
        Star.dec > 5,
        Star.ra <= 2,
        Star.hip.is_null(),
        Star.name.is_in(["stuff", "sirius", "fakestar"]),
        (Star.name == "wrong") | (Star.name == "fakestar"),
        Star.name != "noname",
        (Star.name == "bellatrix") | ((Star.name == "fakestar") & (Star.magnitude < 5)),
    ]
    assert all([e.evaluate(star) for e in expressions])


def test_star_false_expressions():
    star = Star(ra=2, dec=20, magnitude=4, bv=2.12, name="fakestar")

    expressions = [
        Star.ra > 4,
        Star.dec < 5,
        Star.hip.is_not_null(),
        Star.name.is_not_in(["stuff", "sirius", "fakestar"]),
        (Star.name == "wrong") | (Star.name != "fakestar"),
    ]
    assert not any([e.evaluate(star) for e in expressions])


def test_model_manager_get():
    sirius = Star.get(name="Sirius")

    assert sirius.magnitude == -1.44
    assert sirius.hip == 32349


def test_model_manager_get_raises_exception():
    with pytest.raises(ValueError):
        Star.get(name=None)


def test_model_manager_find():
    hipstars = Star.find(where=[Star.hip.is_not_null()])
    assert len(hipstars) == 118_218

    names = {"Sirius", "Bellatrix", "Castor", "Vega"}
    bright = Star.find(where=[Star.name.is_in(names)])
    assert len(bright) == 4
    assert set([s.name for s in bright]) == names


def test_model_moon_get():
    dt = timezone("UTC").localize(datetime(2023, 8, 27, 23, 0, 0, 0))
    m = Moon.get(dt)
    assert m.ra == 19.502411822774185
    assert m.dec == -26.96492167310071
    assert m.apparent_size == 0.5480758923848209
