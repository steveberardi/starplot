import hashlib
from pathlib import Path

from datetime import datetime

from starplot.charts import create_star_chart
from starplot.models import SkyObject

HERE = Path(__file__).resolve().parent
DATA_PATH = HERE / "data"


def assert_md5_equal(filename_1, filename_2):
    with open(filename_1, "rb") as f1, open(filename_2, "rb") as f2:
        md5_f1 = hashlib.md5(f1.read()).hexdigest()
        md5_f2 = hashlib.md5(f2.read()).hexdigest()
        assert md5_f1 == md5_f2


def test_creates_star_chart_correctly():
    filename = DATA_PATH / "actual.png"
    create_star_chart(
        lat=32.97,
        lon=-117.038611,
        dt=datetime(2023, 6, 20, 4),
        tz_identifier="UTC",
        filename=filename,
    )
    assert_md5_equal(filename, DATA_PATH / "expected.png")


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
    assert_md5_equal(filename, DATA_PATH / "expected-extra.png")
