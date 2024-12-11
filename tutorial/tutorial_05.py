from datetime import datetime
from pytz import timezone
from starplot import OpticPlot
from starplot.optics import Binoculars
from starplot.styles import PlotStyle, extensions

dt = datetime.now(timezone("US/Pacific")).replace(2024, 4, 8, 21, 0, 0)

style = PlotStyle().extend(
    extensions.GRAYSCALE_DARK,
    extensions.OPTIC,
)

p = OpticPlot(
    # target location - M44
    ra=8.667,
    dec=19.67,
    # observer location - Palomar Mountain
    lat=33.363484,
    lon=-116.836394,
    # define the optic - 10x binoculars with a 65 degree field of view
    optic=Binoculars(
        magnification=10,
        fov=65,
    ),
    dt=dt,
    style=style,
    resolution=2048,
    autoscale=True,
)
p.stars(mag=12, catalog="big-sky-mag11", bayer_labels=True)

p.export("tutorial_05.png", padding=0.1, transparent=True)
