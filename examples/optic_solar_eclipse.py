from datetime import datetime
from pytz import timezone

from starplot import Moon, optics, Observer
from starplot.styles import PlotStyle, extensions

# time of partial eclipse. total eclipse started at 15:13:46
eastern = timezone("US/Eastern")
dt = eastern.localize(datetime(2024, 4, 8, 14, 40, 47, 0))

observer = Observer(
    dt=dt,
    lat = 41.482222,  # Cleveland, Ohio
    lon = -81.669722,
)

m = Moon.get(dt=observer.dt, lat=observer.lat, lon=observer.lon)

op = m.create_optic(
    observer=observer,
    optic=optics.Binoculars(magnification=20, fov=65),
    style=PlotStyle().extend(extensions.BLUE_DARK, extensions.OPTIC),
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
