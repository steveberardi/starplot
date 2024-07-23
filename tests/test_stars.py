import pytest

from starplot.data import stars


def test_star_hip_names():
    assert stars.STAR_NAMES[95947] == "Albireo"
    assert stars.STAR_NAMES[11767] == "Polaris"
    assert stars.STAR_NAMES[32349] == "Sirius"
    assert stars.STAR_NAMES[91262] == "Vega"


def test_stars_load_default():
    """By default, stars.load should load the Hipparcos catalog"""
    allstars = stars.load()
    assert len(allstars) == 118_218


def test_stars_load_bigsky_mag11():
    allstars = stars.load(stars.StarCatalog.BIG_SKY_MAG11)
    assert len(allstars) == 981_852


def test_stars_load_unrecognized_catalog():
    with pytest.raises(ValueError, match=r"Unrecognized star catalog."):
        stars.load("hello")
