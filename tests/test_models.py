import pytest

from pydantic import ValidationError

from starplot.models import SkyObject


@pytest.mark.parametrize(
    "kwargs",
    [
        dict(name="hello", ra=1, dec=2),
        dict(name="hello", ra=1, dec=2, style={"marker": {"size": 10}}),
    ],
)
def test_sky_object_valid(kwargs):
    try:
        SkyObject(**kwargs)
    except ValidationError:
        pytest.fail("Unexpected ValidationError")


@pytest.mark.parametrize(
    "kwargs",
    [
        dict(name="hello", ra="r", dec=2),
        dict(name="hello", ra=1, dec=2, style={"marker": {"size": "ten"}}),
    ],
)
def test_sky_object_invalid(kwargs):
    with pytest.raises(ValidationError):
        SkyObject(**kwargs)
