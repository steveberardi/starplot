from datetime import datetime

import pytest

from pytz import timezone
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
        (datetime.now(timezone("UTC")), 50, 50),
        (datetime.now(timezone("UTC")), 90, 180),
        (datetime.now(timezone("America/Los_Angeles")), 33, 118),
        (datetime.now(timezone("America/Chicago")), 44, 98),
    ],
)
def test_valid_params(dt, lat, lon):
    Observer(dt=dt, lat=lat, lon=lon)
