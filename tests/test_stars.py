from unittest.mock import patch

from skyfield.data import hipparcos

from starplot.data import stars


def test_star_hip_names():
    assert stars.hip_names[95947] == "Albireo"
    assert stars.hip_names[11767] == "Polaris"
    assert stars.hip_names[32349] == "Sirius"
    assert stars.hip_names[91262] == "Vega"


@patch("starplot.data.stars.hipparcos.load_dataframe")
@patch("starplot.data.stars._load")
def test_get_star_data_base(loadfile, loadframe):
    """assert local file is used when limiting magnitude is within its range"""
    stars.load()
    loadfile.open.assert_called_with("hip8.gz")
    loadframe.assert_called_once()


@patch("starplot.data.stars.hipparcos.load_dataframe")
@patch("starplot.data.stars._load")
def test_get_star_data_remote(loadfile, loadframe):
    """assert remote file is used when limiting magnitude is outside the local file's range"""
    mag = stars.BASE_LIMITING_MAG + 1
    stars.load(limiting_magnitude=mag)
    loadfile.open.assert_called_with(hipparcos.URL)
    loadframe.assert_called_once()
