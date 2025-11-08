from datetime import datetime
from zoneinfo import ZoneInfo

from starplot import ZenithPlot, Observer, _
from starplot.styles import PlotStyle, extensions

tz = ZoneInfo("America/Los_Angeles")
dt = datetime(2023, 7, 13, 22, 0, tzinfo=tz)  # July 13, 2023 at 10pm PT

observer = Observer(
    dt=dt,
    lat=33.363484,
    lon=-116.836394,
)
p = ZenithPlot(
    observer=observer,
    style=PlotStyle().extend(
        extensions.BLUE_GOLD,
        extensions.GRADIENT_PRE_DAWN,
    ),
    resolution=3600,
    autoscale=True,
)
p.horizon()
p.constellations()
p.stars(where=[_.magnitude < 4.6], where_labels=[_.magnitude < 2.1])

p.galaxies(where=[_.magnitude < 9], true_size=False, where_labels=[False])
p.open_clusters(where=[_.magnitude < 9], true_size=False, where_labels=[False])

p.ecliptic()
p.celestial_equator()
p.milky_way()

p.marker(
    ra=12.36 * 15,
    dec=25.85,
    style={
        "marker": {
            "size": 60,
            "symbol": "circle",
            "fill": "none",
            "color": None,
            "edge_color": "hsl(44, 70%, 73%)",
            "edge_width": 2,
            "line_style": [1, [2, 3]],
            "alpha": 1,
            "zorder": 100,
        },
        "label": {
            "zorder": 200,
            "font_size": 22,
            "font_weight": "bold",
            "font_color": "hsl(44, 70%, 64%)",
            "font_alpha": 1,
            "offset_x": "auto",
            "offset_y": "auto",
            "anchor_point": "top right",
        },
    },
    label="Mel 111",
)
p.constellation_labels()

p.export("star_chart_detail.png", transparent=True, padding=0.1)
