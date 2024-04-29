from datetime import datetime
from pytz import timezone

from starplot import Moon, optics
from starplot.styles import PlotStyle, extensions

# time of partial eclipse. total eclipse started at 15:13:46
eastern = timezone("US/Eastern")
dt = eastern.localize(datetime(2024, 4, 8, 14, 40, 47, 0))

# Cleveland, Ohio
lat = 41.482222
lon = -81.669722

m = Moon.get(dt=dt, lat=lat, lon=lon)

op = m.create_optic(
    lat=lat,
    lon=lon,
    dt=dt,
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
