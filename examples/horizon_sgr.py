from datetime import datetime

from pytz import timezone

from starplot import HorizonPlot, Star, DSO
from starplot.styles import PlotStyle, extensions

style = PlotStyle().extend(
    extensions.BLUE_MEDIUM,
    extensions.MAP,
    {"figure_background_color": "hsl(212, 27%, 48%)"},
)

dt = timezone("US/Pacific").localize(datetime(2024, 8, 30, 21, 0, 0, 0))

p = HorizonPlot(
    altitude=(0, 60),
    azimuth=(175, 275),
    lat=36.606111,  # Lone Pine, California
    lon=-118.079444,
    dt=dt,
    style=style,
    resolution=4000,
    scale=0.9,
)

p.constellations()
p.milky_way()

p.stars(where=[Star.magnitude < 5])
p.messier(where=[DSO.magnitude < 12], true_size=False, label_fn=lambda d: f"M{d.m}")

p.constellation_labels()
p.planets()
p.ecliptic()
p.horizon()
p.gridlines()

p.export("horizon_sgr.png", padding=0.2)
