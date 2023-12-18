from datetime import datetime
from pytz import timezone
from starplot import ZenithPlot, SkyObject
from starplot.styles import PlotStyle, extensions

tz = timezone("America/Los_Angeles")
dt = datetime(2023, 7, 13, 22, 0, tzinfo=tz)  # July 13, 2023 at 10pm PT

p = ZenithPlot(
    lat=32.97,
    lon=-117.038611,
    dt=dt,
    limiting_magnitude=4.6,
    style=PlotStyle().extend(
        extensions.GRAYSCALE,
        extensions.ZENITH,
    ),
    resolution=2000,
    adjust_text=True,
)
p.plot_object(
    SkyObject(
        name="Mel 111",
        ra=12.36,
        dec=25.85,
        style={
            "marker": {
                "size": 10,
                "symbol": "*",
                "fill": "full",
                "color": "red",
                "edge_color": "red",
            }
        },
    )
)
p.export("02_star_chart_extra.png")
