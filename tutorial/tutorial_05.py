from datetime import datetime
from pytz import timezone
from starplot import OpticPlot, DSO, _
from starplot.optics import Binoculars
from starplot.styles import PlotStyle, extensions

dt = datetime.now(timezone("US/Pacific")).replace(2024, 4, 8, 21, 0, 0)

style = PlotStyle().extend(
    extensions.GRAYSCALE_DARK,
    extensions.OPTIC,
)

m45 = DSO.get(m="45")  # lookup The Pleiades (M45)

p = OpticPlot(
    # target location via the DSO model instance
    ra=m45.ra,
    dec=m45.dec,
    # observer location - Palomar Mountain
    lat=33.363484,
    lon=-116.836394,
    # define the optic - 15x binoculars with a 65 degree field of view
    optic=Binoculars(
        magnification=15,
        fov=65,
    ),
    dt=dt,
    style=style,
    resolution=2048,
    autoscale=True,
)
p.stars(where=[_.magnitude < 12])

p.export("tutorial_05.png", padding=0.1, transparent=True)
