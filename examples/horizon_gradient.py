from datetime import datetime

from pytz import timezone

from starplot_fork.src.starplot import HorizonPlot, _
from starplot_fork.src.starplot.styles import PlotStyle, extensions

# The background_color of the map must be set as a RGBA value with full
# transparency (e.g. #ffffff00) for the gradient to render correctly.
# You can use either .extend, as is done here, or a style sheet.
style = PlotStyle().extend(
    extensions.BLUE_GOLD,
    extensions.MAP,
    {"figure_background_color": "#e2b900",
     "background_color": "#ffffff00"},
)

dt = timezone("Europe/London").localize(datetime(2025, 7, 26, 23, 0, 0, 0))

p = HorizonPlot(
    altitude=(0, 60),
    azimuth=(135, 225),
    lat=55.079112,  # Stonehaugh, England
    lon=-2.327469,
    dt=dt,
    style=style,
    resolution=4000,
    scale=0.9,
    color_stops=extensions.GRADIENTS["pre_dawn"]
)

p.constellations()
p.milky_way()

p.stars(
    where=[_.magnitude < 5],
    where_labels=[_.magnitude < 2],
    style__marker__symbol="star_4"
    )

p.messier(where=[_.magnitude < 11], true_size=False, label_fn=lambda d: f"M{d.m}")

p.constellation_labels()
p.horizon(labels={180: "SOUTH"})
p.gridlines()

p.export("pre_dawn_horizon.png", padding=0.1)
