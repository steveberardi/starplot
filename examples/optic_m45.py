from datetime import datetime
from pytz import timezone
from starplot import OpticPlot, DSO, _
from starplot.callables import color_by_bv
from starplot.optics import Refractor
from starplot.styles import PlotStyle, extensions

dt = datetime.now(timezone("US/Pacific")).replace(2023, 12, 16, 21, 0, 0)

style = PlotStyle().extend(
    extensions.GRAYSCALE_DARK,
    extensions.OPTIC,
)

m45 = DSO.get(m="45")
p = OpticPlot(
    # M45
    ra=m45.ra,
    dec=m45.dec,
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
    resolution=4096,
    autoscale=True,
)
p.stars(
    where=[_.magnitude < 12],
    color_fn=color_by_bv,
)
p.info()
p.export("optic_m45.png", padding=0.1, transparent=True)
