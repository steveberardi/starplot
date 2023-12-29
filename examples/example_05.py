from datetime import datetime
from pytz import timezone
from starplot import OpticPlot
from starplot.optics import Refractor
from starplot.styles import PlotStyle, extensions

dt = datetime.now(timezone("US/Pacific")).replace(2023, 12, 16, 21, 0, 0)

style = PlotStyle().extend(
    extensions.MINIMAL,
    extensions.GRAYSCALE_DARK,
    extensions.OPTIC,
)

p = OpticPlot(
    # M45
    ra=3.783611,
    dec=24.11667,
    lat=33.363484,
    lon=-116.836394,
    # Refractor Telescope
    optic=Refractor(
        focal_length=430,
        eyepiece_focal_length=11,
        eyepiece_fov=82,
    ),
    dt=dt,
    limiting_magnitude=12,
    style=style,
    resolution=1600,
    include_info_text=True,
    colorize_stars=True,
)

p.export("05_optic_m45.png", padding=0.3)
