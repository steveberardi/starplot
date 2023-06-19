import time
from datetime import datetime, timedelta

from starplot.charts import create_star_chart
from starplot.styles import BLUE, GRAYSCALE, CHALK, RED
from starplot.models import SkyObject

start_time = time.time()


def create_example():
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
        dt=datetime.now().replace(hour=22),
        # dt=datetime(2023, 12, 28).replace(hour=22),
        # dt=datetime(1983, 6, 8),
        tz_identifier="America/Los_Angeles",
        filename="temp.png",
        style=BLUE,
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


def create_365():
    for d in range(365):
        dt = datetime(2023, 1, 1) + timedelta(days=d)
        day_of_year = dt.strftime("%j")

        print(f"Day: {day_of_year}")

        create_star_chart(
            lat=32.97,
            lon=-117.038611,
            dt=dt.replace(hour=4, minute=0),
            tz_identifier="UTC",
            filename=f"temp/day-{day_of_year}.png",
            style=BLUE,
        )


# create_style_examples()
# create_365()
create_example()

print(f"Total run time: {time.time() - start_time}")
