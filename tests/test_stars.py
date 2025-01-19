import pytest

from starplot.data import stars


def test_star_hip_names():
    assert stars.STAR_NAMES[95947] == "Albireo"
    assert stars.STAR_NAMES[11767] == "Polaris"
    assert stars.STAR_NAMES[32349] == "Sirius"
    assert stars.STAR_NAMES[91262] == "Vega"


def test_stars_load_default():
    """By default, stars.load should load the Big Sky MAG-11 catalog"""
    result = stars.load()
    df = result.to_pandas()
    assert len(df) == 981_853


def test_stars_load_unrecognized_catalog():
    with pytest.raises(ValueError, match=r"Unrecognized star catalog."):
        stars.load(catalog="hello")
