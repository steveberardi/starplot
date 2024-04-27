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
    "dms,expected",
    [
        ("-05:20:30", -5.341667),
        ("20:00:00", 20),
        ("-20:00:00", -20),
        ("-00:30:36", -0.51),
    ],
)
def test_dec_str_to_float(dms, expected):
    assert utils.dec_str_to_float(dms) == expected


@pytest.mark.parametrize(
    "lon,ra",
    [
        (0, (0, 0, 0)),
        (-60, (4, 0, 0)),
        (-64, (4, 15, 59)),
        (100, (17, 19, 59)),
        (180, (12, 0, 0)),
    ],
)
def test_lon_to_ra(lon, ra):
    assert utils.lon_to_ra_hms(lon) == ra


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
