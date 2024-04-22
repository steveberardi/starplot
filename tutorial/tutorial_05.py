from datetime import datetime
from pytz import timezone
from starplot import OpticPlot
from starplot.optics import Binoculars
from starplot.styles import PlotStyle, extensions

dt = datetime.now(timezone("US/Pacific")).replace(2024, 4, 8, 21, 0, 0)

style = PlotStyle().extend(
    extensions.GRAYSCALE_DARK,
    extensions.OPTIC,
    {"star": {"marker": {"size": 58}}},  # make the stars bigger
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
    resolution=1600,
)
p.stars(mag=12, catalog="tycho-1", bayer_labels=True)

p.export("tutorial_05.png", padding=0.1, transparent=True)
