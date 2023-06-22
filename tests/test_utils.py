import pytest

from starplot.utils import in_circle


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
