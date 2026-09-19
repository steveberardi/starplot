from datetime import datetime
from zoneinfo import ZoneInfo

from starplot import Moon, Binoculars, Observer
from starplot.styles import PlotStyle, extensions, gradients

# time of partial eclipse. total eclipse started at 15:13:46
dt = datetime(2024, 4, 8, 14, 45, 0, 0, tzinfo=ZoneInfo("US/Eastern"))


observer = Observer(
    dt=dt,
    lat=41.482222,  # Cleveland, Ohio
    lon=-81.669722,
)

m = Moon.get(observer)

op = m.create_optic(
    observer=observer,
    optic=Binoculars(magnification=30, fov=65),
    style=PlotStyle().extend(
        extensions.GRAYSCALE_DARK,
        extensions.OPTIC,
        extensions.GRADIENT_DAYLIGHT,
    ),
)
op.moon(
    true_size=True,
    label=None,
    style__marker__fill={"stops": gradients.NEW_MOON, "type": "radial"},
)
op.sun(
    true_size=True,
    style__marker__fill={"stops": gradients.SUN, "type": "radial"},
    label=None,
)

op.export("optic_solar_eclipse.png")
