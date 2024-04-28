from datetime import datetime
from pytz import timezone
from starplot import OpticPlot
from starplot.callables import color_by_bv
from starplot.optics import Refractor
from starplot.styles import PlotStyle, extensions

dt = datetime.now(timezone("US/Pacific")).replace(2023, 12, 16, 21, 0, 0)

style = PlotStyle().extend(
    extensions.GRAYSCALE_DARK,
    extensions.OPTIC,
)

p = OpticPlot(
    # M45
    ra=3.7912778,
    dec=24.1052778,
    lat=33.363484,
    lon=-116.836394,
    # Refractor Telescope
    optic=Refractor(
        focal_length=430,
        eyepiece_focal_length=11,
        eyepiece_fov=82,
    ),
    dt=dt,
    style=style,
    resolution=1600,
)
p.stars(
    mag=12,
    color_fn=color_by_bv,
)
p.info()
p.export("optic_m45.png", padding=0.1, transparent=True)
