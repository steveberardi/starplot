from pathlib import Path
from datetime import datetime, timezone

import pytest

from starplot import ZenithPlot
from starplot.models import SkyObject

from .utils import assert_hashes_equal

HERE = Path(__file__).resolve().parent
DATA_PATH = HERE / "data"


@pytest.fixture()
def zenith_plot():
    yield ZenithPlot(
        lat=32.97,
        lon=-117.038611,
        dt=datetime(2023, 6, 20, 4, tzinfo=timezone.utc),
        limiting_magnitude=4.6,
        resolution=2048,
    )


def test_zenith_plot_base(zenith_plot):
    filename = DATA_PATH / "actual-zenith-base.png"
    zenith_plot.export(filename)
    assert_hashes_equal(filename, DATA_PATH / "expected-zenith-base.png")


def test_zenith_plot_with_extra_objects(zenith_plot):
    filename = DATA_PATH / "actual-zenith-extra.png"
    obj = SkyObject(
        name="Mel 111",
        ra=12.36,
        dec=25.85,
        style={"marker": {"size": 10, "symbol": "*", "fill": "full", "color": "red"}},
    )
    zenith_plot.plot_object(obj)
    zenith_plot.export(filename)
    assert_hashes_equal(filename, DATA_PATH / "expected-zenith-extra.png")


def test_zenith_plot_with_info_label():
    filename = DATA_PATH / "actual-zenith-info.png"
    zp = ZenithPlot(
        lat=32.97,
        lon=-117.038611,
        dt=datetime(2023, 6, 20, 4, tzinfo=timezone.utc),
        limiting_magnitude=4.6,
        resolution=2048,
        include_info_text=True,
    )
    zp.export(filename)
    assert_hashes_equal(filename, DATA_PATH / "expected-zenith-info.png")
