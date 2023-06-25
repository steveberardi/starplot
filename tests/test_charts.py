from pathlib import Path
from datetime import datetime

import imagehash
from PIL import Image

from starplot.charts import create_star_chart
from starplot.models import SkyObject

HERE = Path(__file__).resolve().parent
DATA_PATH = HERE / "data"


def assert_hash_equal(filename_1, filename_2):
    """Use an image-based hash to determine if the two files are visually similar"""
    hash_1 = imagehash.dhash(Image.open(filename_1))
    hash_2 = imagehash.dhash(Image.open(filename_2))
    assert hash_1 == hash_2


def test_creates_star_chart_correctly():
    filename = DATA_PATH / "actual.png"
    create_star_chart(
        lat=32.97,
        lon=-117.038611,
        dt=datetime(2023, 6, 20, 4),
        tz_identifier="UTC",
        filename=filename,
    )
    assert_hash_equal(filename, DATA_PATH / "expected.png")


def test_creates_star_chart_with_extra_objects():
    filename = DATA_PATH / "actual-extra.png"
    extra = [
        SkyObject(
            name="Mel 111",
            ra=12.36,
            dec=25.85,
            style={
                "marker": {"size": 10, "symbol": "*", "fill": "full", "color": "red"}
            },
        ),
    ]
    create_star_chart(
        lat=32.97,
        lon=-117.038611,
        dt=datetime(2023, 6, 20, 4),
        tz_identifier="UTC",
        filename=filename,
        extra_objects=extra,
    )
    assert_hash_equal(filename, DATA_PATH / "expected-extra.png")

def test_creates_star_chart_with_info_label():
    filename = DATA_PATH / "actual-info.png"
    create_star_chart(
        lat=32.97,
        lon=-117.038611,
        dt=datetime(2023, 6, 20, 4),
        tz_identifier="UTC",
        filename=filename,
        include_info_text=True,
    )
    assert_hash_equal(filename, DATA_PATH / "expected-info.png")
