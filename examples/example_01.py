from datetime import datetime
from pytz import timezone
from starplot import MapPlot, Projection
from starplot.data import constellations
from starplot.styles import PlotStyle, extensions

tz = timezone("America/Los_Angeles")
dt = datetime(2023, 7, 13, 22, 0, tzinfo=tz)  # July 13, 2023 at 10pm PT

p = MapPlot(
    projection=Projection.ZENITH,
    lat=33.363484,
    lon=-116.836394,
    dt=dt,
    ra_min=0,
    ra_max=24,
    dec_min=-90,
    dec_max=90,
    style=PlotStyle().extend(
        extensions.BLUE_MEDIUM,
        extensions.ZENITH,
    ),
    resolution=2000,
)
p.constellations(labels=constellations.CONSTELLATIONS_FULL_NAMES)
p.stars(mag=4.6, mag_labels=2.1)

p.export("01_star_chart.png")
