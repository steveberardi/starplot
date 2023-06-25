from unittest.mock import patch

from skyfield.data import hipparcos

from starplot.stars import hip_names, get_star_data, BASE_LIMITING_MAG


def test_star_hip_names():
    assert hip_names[95947] == "Albireo"
    assert hip_names[11767] == "Polaris"
    assert hip_names[32349] == "Sirius"
    assert hip_names[91262] == "Vega"


@patch("starplot.stars.hipparcos.load_dataframe")
@patch("starplot.stars.load")
def test_get_star_data_base(loadfile, loadframe):
    """assert local file is used when limiting magnitude is within its range"""
    get_star_data()
    loadfile.open.assert_called_with("hip8.gz")
    loadframe.assert_called_once()


@patch("starplot.stars.hipparcos.load_dataframe")
@patch("starplot.stars.load")
def test_get_star_data_remote(loadfile, loadframe):
    """assert remote file is used when limiting magnitude is outside the local file's range"""
    mag = BASE_LIMITING_MAG + 1
    get_star_data(mag)
    loadfile.open.assert_called_with(hipparcos.URL)
    loadframe.assert_called_once()
