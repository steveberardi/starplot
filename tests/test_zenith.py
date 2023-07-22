from pathlib import Path
from datetime import datetime, timezone

import imagehash
from PIL import Image
import pytest

from starplot import ZenithPlot
from starplot.models import SkyObject

HERE = Path(__file__).resolve().parent
DATA_PATH = HERE / "data"


def assert_hash_equal(filename_1, filename_2):
    """Use an image-based hash to determine if the two files are visually similar"""
    hash_1 = imagehash.dhash(Image.open(filename_1))
    hash_2 = imagehash.dhash(Image.open(filename_2))
    assert hash_1 == hash_2


@pytest.fixture()
def zenith_plot():
    yield ZenithPlot(
        lat=32.97,
        lon=-117.038611,
        dt=datetime(2023, 6, 20, 4, tzinfo=timezone.utc),
        limiting_magnitude=4.6,
        resolution=2048,
    )


def test_zenith_plot_default(zenith_plot):
    filename = DATA_PATH / "actual.png"
    zenith_plot.export(filename)
    assert_hash_equal(filename, DATA_PATH / "expected.png")


def test_zenith_plot_with_extra_objects(zenith_plot):
    filename = DATA_PATH / "actual-extra.png"
    obj = SkyObject(
        name="Mel 111",
        ra=12.36,
        dec=25.85,
        style={"marker": {"size": 10, "symbol": "*", "fill": "full", "color": "red"}},
    )
    zenith_plot.plot_object(obj)
    zenith_plot.export(filename)
    assert_hash_equal(filename, DATA_PATH / "expected-extra.png")


def test_zenith_plot_with_info_label():
    filename = DATA_PATH / "actual-info.png"
    zp = ZenithPlot(
        lat=32.97,
        lon=-117.038611,
        dt=datetime(2023, 6, 20, 4, tzinfo=timezone.utc),
        limiting_magnitude=4.6,
        resolution=2048,
        include_info_text=True,
    )
    zp.export(filename)
    assert_hash_equal(filename, DATA_PATH / "expected-info.png")
