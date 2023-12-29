import pytest

from starplot.data import stars


def test_star_hip_names():
    assert stars.hip_names[95947] == "Albireo"
    assert stars.hip_names[11767] == "Polaris"
    assert stars.hip_names[32349] == "Sirius"
    assert stars.hip_names[91262] == "Vega"


def test_stars_load_default():
    """By default, stars.load should load the Hipparcos catalog"""
    allstars = stars.load()
    assert len(allstars) == 118_218


def test_stars_load_tycho_1():
    allstars = stars.load(stars.StarCatalog.TYCHO_1)
    assert len(allstars) == 1_055_115


def test_stars_load_unrecognized_catalog():
    with pytest.raises(ValueError, match=r"Unrecognized star catalog."):
        stars.load("hello")
