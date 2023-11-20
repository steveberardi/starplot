import pytest

from starplot.utils import in_circle, dec_str_to_float


@pytest.mark.parametrize(
    "x,y,expected",
    [
        (0, 0, True),
        (1, 1, False),
        (0.2, 0.8, True),
        (1.01, 0, False),
    ],
)
def test_in_circle(x, y, expected):
    assert in_circle(x, y) == expected


@pytest.mark.parametrize(
    "dms,expected",
    [
        ("-05:20:30", -5.341667),
        ("20:00:00", 20),
        ("-20:00:00", -20),
        ("-00:30:36", -0.51),
    ],
)
def test_dec_str_to_float(dms, expected):
    assert dec_str_to_float(dms) == expected
