import time
from datetime import datetime

from starplot.charts import create_star_chart
from starplot.styles import BLUE, GRAYSCALE, CHALK, RED
from starplot.models import SkyObject

start_time = time.time()

extra = [
    SkyObject(
        name="Mel 111",
        ra=12.36,
        dec=25.85,
        style={"marker": {"size": 10, "symbol": "*", "fill": "full", "color": "red"}},
    ),
]

create_star_chart(
    lat=32.97,
    lon=-117.038611,
    dt=datetime.now().replace(hour=22),
    # dt=datetime(2023, 12, 28).replace(hour=22),
    # dt=datetime(2023, 2, 8),
    tz_identifier="America/Los_Angeles",
    filename="temp.png",
    style=GRAYSCALE,
    extra_objects=extra,
)


def create_style_examples():
    styles = {
        "blue": BLUE,
        "grayscale": GRAYSCALE,
        "chalk": CHALK,
        "red": RED,
    }
    for name, style in styles.items():
        create_star_chart(
            lat=32.97,
            lon=-117.038611,
            dt=datetime.now().replace(hour=22),
            # dt=datetime(2023, 12, 28).replace(hour=22),
            # dt=datetime(2023, 2, 8),
            tz_identifier="America/Los_Angeles",
            filename=f"examples/starchart-{name}.png",
            style=style,
        )


# create_style_examples()

print(f"Total run time: {time.time() - start_time}")
