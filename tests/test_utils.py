import pytest

from starplot import utils


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
    assert utils.in_circle(x, y) == expected


@pytest.mark.parametrize(
    "bv,hexcolor",
    [
        (-0.03, "#ccd8ff"),
        (-0.3, "#a3b9ff"),
        (-0.4, "#9bb2ff"),
        (0.74, "#ffeddb"),
        (1.21, "#ffdfb8"),
        (1.85, "#ffa94b"),
        (5, None),
    ],
)
def test_bv_to_hex_color(bv, hexcolor):
    if hexcolor is None:
        assert utils.bv_to_hex_color(bv) is None
    else:
        assert utils.bv_to_hex_color(bv) == hexcolor


@pytest.mark.parametrize(
    "az,expected",
    [
        (360, "N"),
        (0, "N"),
        (20, "N"),
        (45, "NE"),
        (90, "E"),
        (100, "E"),
        (120, "SE"),
        (150, "SE"),
        (180, "S"),
        (190, "S"),
        (220, "SW"),
        (270, "W"),
        (280, "NW"),
        (320, "N"),
        (350, "N"),
    ],
)
def test_azimuth_to_string(az, expected):
    assert utils.azimuth_to_string(az) == expected


@pytest.mark.parametrize(
    "value,min_val,max_val,expected",
    [
        (5, 0, 10, 0.5),
        (0, 0, 10, 0),
        (10, 0, 10, 1),
        (-5, 0, 10, -0.5),  # extrapolates below the range
        (15, 0, 10, 1.5),  # extrapolates above the range
    ],
)
def test_normalize(value, min_val, max_val, expected):
    assert utils.normalize(value, min_val, max_val) == expected


@pytest.mark.parametrize(
    "start,end,t,expected",
    [
        (0, 10, 0, 0),
        (0, 10, 1, 10),
        (0, 10, 0.5, 5),
        (10, 0, 0.5, 5),
        (0, 10, 1.5, 15),  # extrapolates beyond t=1
    ],
)
def test_lerp(start, end, t, expected):
    assert utils.lerp(start, end, t) == expected


@pytest.mark.parametrize(
    "hex_color,expected",
    [
        ("#ff9523", (255, 149, 35)),
        ("000000", (0, 0, 0)),  # works without a leading '#' too
        ("#FFFFFF", (255, 255, 255)),
        ("#0a1b2c", (10, 27, 44)),
    ],
)
def test_hex_to_rgb(hex_color, expected):
    assert utils.hex_to_rgb(hex_color) == expected


@pytest.mark.parametrize(
    "hex_color,amount,expected",
    [
        ("#000000", 0, "#000000"),  # amount=0 leaves the color unchanged
        ("#000000", 1, "#ffffff"),  # amount=1 blends all the way to white
        ("#000000", 0.5, "#808080"),
        ("#ff9523", 0.3, "#ffb565"),
        ("#ffffff", 0.5, "#ffffff"),  # already white, stays white
    ],
)
def test_lighten_hex_color(hex_color, amount, expected):
    assert utils.lighten_hex_color(hex_color, amount) == expected


@pytest.mark.parametrize(
    "where,expected",
    [
        (False, [False]),
        (True, []),
        (None, []),
        ([], []),
        (["a", "b"], ["a", "b"]),
    ],
)
def test_normalize_where(where, expected):
    assert utils.normalize_where(where) == expected


@pytest.mark.parametrize(
    "start,end,num_points,expected",
    [
        ((0, 0), (10, 0), 5, [(0, 0), (2.5, 0), (5, 0), (7.5, 0), (10, 0)]),
        ((0, 0), (10, 0), 2, [(0, 0), (10, 0)]),  # just the two endpoints
        ((0, 0), (10, 10), 3, [(0, 0), (5, 5), (10, 10)]),
        ((0, 0), (0, 0), 3, [(0, 0), (0, 0), (0, 0)]),  # zero-length line
    ],
)
def test_points_on_line(start, end, num_points, expected):
    assert utils.points_on_line(start, end, num_points) == expected


def test_points_on_line_defaults_to_100_points():
    assert len(utils.points_on_line((0, 0), (10, 10))) == 100
