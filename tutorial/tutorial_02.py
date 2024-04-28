from datetime import datetime
from pytz import timezone
from starplot import MapPlot, Projection

tz = timezone("America/Los_Angeles")
dt = datetime(2023, 7, 13, 22, 0, tzinfo=tz)  # July 13, 2023 at 10pm PT

p = MapPlot(
    projection=Projection.ZENITH,
    lat=33.363484,
    lon=-116.836394,
    dt=dt,
    resolution=2600,
)
p.constellations()
p.stars(mag=4.6)

p.export("tutorial_02.png", transparent=True)
