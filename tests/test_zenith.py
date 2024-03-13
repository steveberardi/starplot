from pathlib import Path
from datetime import datetime

import pytest
from pytz import timezone

from starplot import styles
from starplot.map import MapPlot, Projection

from .utils import colorhash, dhash

HERE = Path(__file__).resolve().parent
DATA_PATH = HERE / "data"

STYLE = styles.PlotStyle().extend(
    styles.extensions.BLUE_MEDIUM,
    styles.extensions.ZENITH,
)

JUNE_2023 = datetime.now(timezone("US/Pacific")).replace(2023, 6, 20, 21, 0, 0)

RESOLUTION = 2400


@pytest.fixture()
def zenith_plot():
    p = MapPlot(
        projection=Projection.ZENITH,
        lat=32.97,
        lon=-117.038611,
        dt=JUNE_2023,
        style=STYLE,
        resolution=RESOLUTION,
    )
    p.stars(mag=4.6)
    p.constellations()
    p.ecliptic()
    p.celestial_equator()
    yield p


def test_zenith_base(zenith_plot):
    filename = DATA_PATH / "zenith-base.png"
    zenith_plot.export(filename)

    assert dhash(filename) == "1359cca68a946927"
    assert colorhash(filename) == "06007000000"
