from datetime import datetime
from zoneinfo import ZoneInfo

import numpy as np
import pytest
from pydantic import ValidationError
from skyfield.api import Star as SkyfieldStar

from starplot import Observer


def test_raises_exception_on_tz_naive():
    with pytest.raises(ValidationError, match=r"Input should have timezone info"):
        Observer(dt=datetime.now())  # noqa DTZ005


def test_raises_exception_on_invalid_lat_lon():
    with pytest.raises(
        ValidationError, match=r"Input should be less than or equal to 90"
    ):
        Observer(lat=99)

    with pytest.raises(
        ValidationError, match=r"Input should be greater than or equal to -90"
    ):
        Observer(lat=-99)

    with pytest.raises(
        ValidationError, match=r"Input should be less than or equal to 180"
    ):
        Observer(lon=399)

    with pytest.raises(
        ValidationError, match=r"Input should be greater than or equal to -180"
    ):
        Observer(lon=-399)


@pytest.mark.parametrize(
    "dt,lat,lon",
    [
        (datetime.now(ZoneInfo("UTC")), 50, 50),
        (datetime.now(ZoneInfo("UTC")), 90, 180),
        (datetime.now(ZoneInfo("America/Los_Angeles")), 33, 118),
        (datetime.now(ZoneInfo("America/Chicago")), 44, 98),
    ],
)
def test_valid_params(dt, lat, lon):
    Observer(dt=dt, lat=lat, lon=lon)


def test_lst():
    tz = ZoneInfo("America/Los_Angeles")
    dt = datetime(2025, 8, 2, 7, 54, 0, 0, tzinfo=tz)
    obs = Observer(dt=dt, lat=35, lon=-117.0634)
    assert obs.lst == pytest.approx(57.89127678132414, rel=1e-6)


def test_immutable():
    obs = Observer(lat=35, lon=-117.0634)
    with pytest.raises(ValidationError, match=r"Instance is frozen"):
        obs.lat = 90


def test_apparent_refraction_is_continuous_across_the_horizon():
    # GIVEN an observer and a line of stars crossing the horizon
    observer = Observer(
        dt=datetime(2025, 12, 21, 19, 0, tzinfo=ZoneInfo("America/Los_Angeles")),
        lat=32.9628,
        lon=-117.0359,
    )
    dec = np.linspace(-4, 14, 1801)
    stars = SkyfieldStar(ra_hours=np.full(dec.shape, 7.46), dec_degrees=dec)

    # WHEN calculating their apparent and geometric altitudes
    _, alt = observer._apparent(stars)
    geometric = observer.observe("de440s.bsp")(stars).apparent().altaz()[0].degrees

    # THEN the refraction lift never jumps between neighboring stars
    lift = alt - geometric
    assert np.abs(np.diff(lift)).max() < 0.01

    # AND the lift is constant below the horizon, and positive everywhere
    assert np.allclose(lift[geometric < -1], lift[geometric < -1][0])
    assert (lift > 0).all()
