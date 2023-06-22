import hashlib
from pathlib import Path

from datetime import datetime

from starplot.charts import create_star_chart

HERE = Path(__file__).resolve().parent
DATA_PATH = HERE / "data"


def test_creates_star_chart_correctly():
    filename = DATA_PATH / "temp.png"
    create_star_chart(
        lat=32.97,
        lon=-117.038611,
        dt=datetime(2023, 6, 20, 4),
        tz_identifier="UTC",
        filename=filename,
    )

    with open(filename, "rb") as actual, open(
        DATA_PATH / "expected.png", "rb"
    ) as expected:
        md5_actual = hashlib.md5(actual.read()).hexdigest()
        md5_expected = hashlib.md5(expected.read()).hexdigest()
        assert md5_actual == md5_expected
