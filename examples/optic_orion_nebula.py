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
    # Orion Nebula
    ra=5.583,
    dec=-5.383,
    lat=32.97,
    lon=-117.038611,
    # TV-85
    optic=Refractor(
        focal_length=600,
        eyepiece_focal_length=11,
        eyepiece_fov=100,
    ),
    dt=dt,
    style=style,
    resolution=1800,
)
p.stars(mag=15, color_fn=color_by_bv, bayer_labels=True)
p.dsos(mag=4.1, labels=None)
p.info()
p.export("optic_orion_nebula.png", padding=0.1, transparent=True)
