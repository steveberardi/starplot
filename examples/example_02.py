from datetime import datetime
from pytz import timezone
from starplot import MapPlot, Projection
from starplot.styles import PlotStyle, extensions

tz = timezone("America/Los_Angeles")
dt = datetime(2023, 7, 13, 22, 0, tzinfo=tz)  # July 13, 2023 at 10pm PT

p = MapPlot(
    projection=Projection.ZENITH,
    lat=33.363484,
    lon=-116.836394,
    dt=dt,
    style=PlotStyle().extend(
        extensions.BLUE_MEDIUM,
        extensions.ZENITH,
    ),
    resolution=2600,
)
p.constellations()
p.stars(mag=5.6, mag_labels=2.1)

p.dsos(mag=9, null=True, true_size=True, labels=None)
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
        },
    },
)

p.export("02_star_chart_extra.png", transparent=True)
