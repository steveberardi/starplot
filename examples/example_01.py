from datetime import datetime
from pytz import timezone
from starplot import ZenithPlot
from starplot.styles import PlotStyle, extensions

tz = timezone("America/Los_Angeles")
dt = datetime(2023, 7, 13, 22, 0, tzinfo=tz)  # July 13, 2023 at 10pm PT

p = ZenithPlot(
    lat=33.363484,
    lon=-116.836394,
    dt=dt,
    limiting_magnitude=4.6,
    style=PlotStyle().extend(
        extensions.BLUE_MEDIUM,
        extensions.ZENITH,
    ),
    resolution=2000,
    adjust_text=True,
)
p.export("01_star_chart.png")
