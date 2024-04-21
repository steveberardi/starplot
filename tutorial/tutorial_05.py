from datetime import datetime
from pytz import timezone
from starplot import OpticPlot
from starplot.optics import Refractor
from starplot.styles import PlotStyle, extensions

dt = datetime.now(timezone("US/Pacific")).replace(2024, 4, 8, 21, 0, 0)

style = PlotStyle().extend(
    extensions.GRAYSCALE_DARK,
    extensions.OPTIC,
)

p = OpticPlot(
    # M44
    ra=8.667,
    dec=19.67,
    lat=33.363484,
    lon=-116.836394,
    # Refractor Telescope
    optic=Refractor(
        focal_length=560,
        eyepiece_focal_length=14,
        eyepiece_fov=82,
    ),
    dt=dt,
    style=style,
    resolution=1600,
)
p.stars(mag=14, catalog="tycho-1", bayer_labels=True)
# p.info()
p.export("tutorial_05.png", padding=0.1, transparent=True)
