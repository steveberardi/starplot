from datetime import datetime
from pytz import timezone
from starplot import MapPlot, Projection, Star, DSO
from starplot.styles import PlotStyle, extensions

tz = timezone("America/Los_Angeles")
dt = datetime(2023, 7, 13, 22, 0, tzinfo=tz)  # July 13, 2023 at 10pm PT

p = MapPlot(
    projection=Projection.ZENITH,
    lat=33.363484,
    lon=-116.836394,
    dt=dt,
    style=PlotStyle().extend(
        extensions.NORD,
    ),
    resolution=3600,
)
p.constellations()
p.stars(mag=4.6, where_labels=[Star.magnitude < 2.1])

p.galaxies(where=[DSO.magnitude < 10], true_size=False, labels=None)
p.open_clusters(where=[DSO.magnitude < 10], true_size=False, labels=None)

p.constellation_borders()
p.ecliptic()
p.celestial_equator()
p.milky_way()

p.marker(
    ra=12.36,
    dec=25.85,
    label="Mel 111",
    style={
        "marker": {
            "size": 28,
            "symbol": "circle",
            "fill": "full",
            "color": "#ed7eed",
            "edge_color": "#e0c1e0",
            "alpha": 0.4,
            "zorder": 100,
        },
        "label": {
            "zorder": 200,
            "font_size": 12,
            "font_weight": "bold",
            "font_color": "ed7eed",
            "font_alpha": 0.8,
        },
    },
)
p.horizon()

p.export("star_chart_detail.png", transparent=True, padding=0.1)
