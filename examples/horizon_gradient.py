from datetime import datetime
from zoneinfo import ZoneInfo

from starplot import HorizonPlot, Observer, _
from starplot.styles import PlotStyle, extensions

style = PlotStyle().extend(
    extensions.BLUE_GOLD,
    extensions.MAP,
    extensions.GRADIENT_PRE_DAWN,
)

dt = datetime(2025, 7, 26, 23, 30, 0, 0, tzinfo=ZoneInfo("Europe/London"))

observer = Observer(
    lat=55.079112,  # Stonehaugh, England
    lon=-2.327469,
    dt=dt,
)

p = HorizonPlot(
    altitude=(0, 60),
    azimuth=(135, 225),
    observer=observer,
    style=style,
    resolution=3200,
    scale=0.9,
)

p.constellations()
p.milky_way()

p.stars(
    where=[_.magnitude < 5],
    where_labels=[_.magnitude < 2],
    style__marker__symbol="star_4",
)

p.messier(where=[_.magnitude < 11], true_size=False)

p.constellation_labels()
p.horizon(labels={180: "SOUTH"})

p.export("horizon_gradient.png", padding=0.1)
