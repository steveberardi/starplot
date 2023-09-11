from datetime import datetime
from pytz import timezone
from starplot import ZenithPlot
from starplot.styles import PlotStyle, extensions

tz = timezone("America/Los_Angeles")

p = ZenithPlot(
    lat=33.363484,
    lon=-116.836394,
    dt=datetime.now(tz).replace(hour=22),
    limiting_magnitude=4.6,
    style=PlotStyle().extend(
        extensions.BLUE_MEDIUM,
        extensions.ZENITH,
    ),
    resolution=2000,
)
p.export("01_star_chart.png")