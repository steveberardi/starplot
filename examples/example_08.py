from datetime import datetime
from pytz import timezone
from starplot import MapPlot, Projection
from starplot.styles import PlotStyle, extensions, MarkerSymbolEnum

style = PlotStyle().extend(
    extensions.BLUE_MEDIUM,
    extensions.MAP,
)

tz = timezone("Europe/Amsterdam")
dt = datetime(2024, 1, 20, 22, 00, tzinfo=tz)  # July 13, 2023 at 10pm PT
lat, lon = (52.377956, 4.897070)

p = MapPlot(
    projection=Projection.ORTHOGRAPHIC,
    lat=lat,
    lon=lon,
    dt=dt,
    ra_min=0,
    ra_max=24,
    dec_min=-90,
    dec_max=90,
    limiting_magnitude=3.6,
    style=style,
    resolution=1400,
    dso_types=[],  # this is one way to hide all deep sky objects
)

p.export("08_orthographic.png", padding=0.2)
