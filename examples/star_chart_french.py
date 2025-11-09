from datetime import datetime
from zoneinfo import ZoneInfo

from starplot import ZenithPlot, Observer, settings, _
from starplot.styles import PlotStyle, extensions

tz = ZoneInfo("Europe/Paris")
dt = datetime(2025, 11, 18, 21, 0, tzinfo=tz)

settings.language = "fr"

observer = Observer(
    dt=dt,
    lat=48.8575,  # Paris, France
    lon=2.3514,
)
p = ZenithPlot(
    observer=observer,
    style=PlotStyle().extend(
        extensions.BLUE_MEDIUM,
    ),
    resolution=3600,
    autoscale=True,
)
p.horizon()
p.constellations()
p.stars(where=[_.magnitude < 4.86], where_labels=[_.magnitude < 2.4])
p.messier(where=[_.magnitude < 10], true_size=False)
p.ecliptic()
p.celestial_equator()
p.milky_way()
p.constellation_labels()

p.export("star_chart_french.png", transparent=True, padding=0.1)
