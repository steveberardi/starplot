from datetime import datetime
from pytz import timezone

from starplot import MapPlot, Projection, Star, DSO
from starplot.styles import PlotStyle, extensions


style = PlotStyle().extend(
    extensions.BLUE_MEDIUM,
    extensions.MAP,
)

tz = timezone("America/Los_Angeles")
dt = datetime(2024, 10, 19, 21, 00, tzinfo=tz)

p = MapPlot(
    projection=Projection.ORTHOGRAPHIC,
    lat=32.97,
    lon=-117.038611,
    dt=dt,
    ra_min=0,
    ra_max=24,
    dec_min=-90,
    dec_max=90,
    style=style,
    scale=0.9,  # lower the scale since it shows a large area
)
p.gridlines(labels=False)
p.constellations(
    style={"label": {"font_alpha": 0.4}},
)
p.constellation_borders()

p.stars(mag=7.86, where_labels=[Star.magnitude < 6])
p.open_clusters(where=[DSO.magnitude < 12], true_size=False, labels=None)
p.galaxies(where=[DSO.magnitude < 12], true_size=False, labels=None)
p.nebula(where=[DSO.magnitude < 12], true_size=False, labels=None)

p.ecliptic()
p.celestial_equator()
p.milky_way()
p.planets()

p.export("map_orthographic.png", padding=0.3, transparent=True)
