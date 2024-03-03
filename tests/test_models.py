import pytest

from pydantic import ValidationError

from starplot.models import Star


@pytest.mark.parametrize(
    "kwargs",
    [
        dict(ra=1, dec=2, magnitude=-1.2),
        dict(ra=1.6, dec=2.6, magnitude=10, bv=2.3, hip=1201),
    ],
)
def test_star_valid(kwargs):
    try:
        s = Star(**kwargs)
        for k, v in kwargs.items():
            assert getattr(s, k) == v
    except ValidationError:
        pytest.fail("Unexpected ValidationError")


@pytest.mark.parametrize(
    "kwargs",
    [
        dict(ra="r", dec=2, magnitude=3),
        dict(ra=1, dec=2, magnitude=4, hip=1.234),
    ],
)
def test_star_invalid(kwargs):
    with pytest.raises(ValidationError):
        Star(**kwargs)
