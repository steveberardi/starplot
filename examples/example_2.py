from datetime import datetime
from pytz import timezone
from starplot import ZenithPlot, SkyObject
from starplot.styles import PlotStyle, extensions

tz = timezone("America/Los_Angeles")

p = ZenithPlot(
    lat=32.97,
    lon=-117.038611,
    dt=datetime.now(tz).replace(hour=22),
    limiting_magnitude=4.6,
    style=PlotStyle().extend(
        extensions.GRAYSCALE,
        extensions.ZENITH,
    ),
    resolution=2000,
)
p.plot_object(
    SkyObject(
        name="Mel 111",
        ra=12.36,
        dec=25.85,
        style={
            "marker": {"size": 10, "symbol": "*", "fill": "full", "color": "red"}
        },
    )
)
p.export("02_star_chart_extra.png")