from datetime import datetime
from zoneinfo import ZoneInfo

from starplot import OpticPlot, Observer, DSO, _
from starplot.models import Binoculars
from starplot.styles import PlotStyle, extensions

tz = ZoneInfo("US/Pacific")
dt = datetime(2024, 4, 8, 21, 0, 0, tzinfo=tz)

observer = Observer(
    dt=dt,
    lat=33.363484,  # Palomar Mountain
    lon=-116.836394,
)

style = PlotStyle().extend(
    extensions.GRAYSCALE_DARK,
    extensions.OPTIC,
)

m45 = DSO.get(m="45")  # lookup The Pleiades (M45)

p = OpticPlot(
    observer=observer,
    # target location via the DSO model instance
    ra=m45.ra,
    dec=m45.dec,
    # define the optic - 15x binoculars with a 65 degree field of view
    optic=Binoculars(
        magnification=15,
        fov=65,
    ),
    style=style,
    resolution=2048,
    autoscale=True,
)
p.stars(where=[_.magnitude < 12])

p.export("tutorial_05.png", padding=0.1, transparent=True)
