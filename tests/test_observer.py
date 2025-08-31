from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from pydantic import ValidationError

from starplot import Observer


def test_raises_exception_on_tz_naive():
    with pytest.raises(ValidationError, match=r"Input should have timezone info"):
        Observer(dt=datetime.now())


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
    assert obs.lst == 57.89127678132414
