from datetime import datetime
from pytz import timezone

from starplot import MapPlot, Orthographic, Observer, _
from starplot.styles import PlotStyle, extensions


style = PlotStyle().extend(
    extensions.BLUE_MEDIUM,
    extensions.MAP,
)

tz = timezone("America/Los_Angeles")
dt = datetime(2024, 10, 19, 21, 00, tzinfo=tz)

observer = Observer(
    dt=dt,
    lat=32.97,
    lon=-117.038611,
)
p = MapPlot(
    projection=Orthographic(
        center_ra=observer.lst,
        center_dec=observer.lat,
    ),
    observer=observer,
    style=style,
    scale=0.9,  # lower the scale since it shows a large area
)
p.gridlines(labels=False)
p.constellations()
p.constellation_borders()

p.stars(where=[_.magnitude < 8], where_labels=[_.magnitude < 5])
p.open_clusters(where=[_.magnitude < 12], true_size=False, where_labels=[False])
p.galaxies(where=[_.magnitude < 12], true_size=False, where_labels=[False])
p.nebula(where=[_.magnitude < 12], true_size=False, where_labels=[False])

p.constellation_labels(style__font_alpha=0.4)
p.ecliptic()
p.celestial_equator()
p.milky_way()
p.planets()

p.export("map_orthographic.png", padding=0.3, transparent=True)
