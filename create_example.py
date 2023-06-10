import time
from datetime import datetime

from starplot.charts import create_star_chart
from starplot.styles import BLUE, MONO, CHALK, RED


start_time = time.time()

styles = [
    ("blue", BLUE),
    # ("chalk", CHALK),
    # ("mono", MONO),
    # ("red", RED),
]

for n, style in styles:
    create_star_chart(
        lat=32.97,
        lon=-117.038611,
        dt=datetime.now(),
        # dt=datetime(2023, 10, 28),
        # dt=datetime(2023, 2, 8),
        tz_identifier="America/Los_Angeles", 
        filename=f"examples/starchart-{n}.png",
        style=style,
    )

print(f"Total run time: {time.time() - start_time}")
