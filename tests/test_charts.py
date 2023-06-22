import hashlib
import tempfile

from datetime import datetime

from starplot.charts import create_star_chart

def test_creates_star_chart_correctly():
    with tempfile.NamedTemporaryFile() as tmp:
        create_star_chart(
            lat=32.97,
            lon=-117.038611,
            dt=datetime(2023, 6, 20, 4),
            tz_identifier="UTC",
            filename=tmp.name,
        )
        md = hashlib.md5(tmp.read()).hexdigest()
        assert md == "d41d8cd98f00b204e9800998ecf8427e"



