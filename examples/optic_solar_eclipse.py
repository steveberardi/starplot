from datetime import datetime
from zoneinfo import ZoneInfo

from starplot import Moon, Binoculars, Observer
from starplot.styles import PlotStyle, extensions

# time of partial eclipse. total eclipse started at 15:13:46
dt = datetime(2024, 4, 8, 14, 40, 47, 0, tzinfo=ZoneInfo("US/Eastern"))


observer = Observer(
    dt=dt,
    lat=41.482222,  # Cleveland, Ohio
    lon=-81.669722,
)

m = Moon.get(dt=observer.dt, lat=observer.lat, lon=observer.lon)

op = m.create_optic(
    observer=observer,
    optic=Binoculars(magnification=20, fov=65),
    style=PlotStyle().extend(
        extensions.GRAYSCALE_DARK,
        extensions.OPTIC,
        extensions.GRADIENT_DAYLIGHT,
    ),
    resolution=2000,
)
op.moon(
    true_size=True,
    show_phase=True,
    label=None,
)
op.sun(
    true_size=True,
    style__marker__color="#ffd22e",
    label=None,
)

op.export("optic_solar_eclipse.png", padding=0.1, transparent=True)
