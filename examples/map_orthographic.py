from datetime import datetime
from pytz import timezone
from starplot import MapPlot, Projection, Star
from starplot.data import constellations
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
    resolution=3200,
)
p.gridlines(labels=False)
p.stars(mag=7.86, where_labels=[Star.magnitude < 6])
p.open_clusters(mag=8, true_size=False, labels=None)
p.galaxies(mag=8, true_size=False, labels=None)
p.nebula(mag=8, true_size=True, labels=None)
p.constellations(
    labels=constellations.CONSTELLATIONS_FULL_NAMES,
    style={"label": {"font_size": 9, "font_alpha": 0.8}},
)
p.constellation_borders()
p.ecliptic()
p.celestial_equator()
p.milky_way()
p.planets()
p.adjust_text()

p.export("map_orthographic.png", padding=0.3, transparent=True)
