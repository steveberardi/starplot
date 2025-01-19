from datetime import datetime
from pytz import timezone

from starplot import Moon, optics, _
from starplot.styles import PlotStyle, extensions

dt = datetime.now(timezone("US/Pacific")).replace(2024, 8, 20, 21, 0, 0)

# Julian, CA
lat = 33.070833
lon = -116.585556

m = Moon.get(dt=dt, lat=lat, lon=lon)

op = m.create_optic(
    lat=lat,
    lon=lon,
    dt=dt,
    optic=optics.Binoculars(magnification=15, fov=65),
    style=PlotStyle().extend(extensions.GRAYSCALE_DARK, extensions.OPTIC),
    resolution=2000,
    autoscale=True,
)
op.moon(
    true_size=True,
    show_phase=True,
)
op.planets(
    true_size=True,
    style__marker__color="#ffe785",
    style__label__offset_x=6,
    style__label__offset_y=-6,
)
op.stars(where=[_.magnitude < 12])

op.export("optic_moon_saturn.png", padding=0.1, transparent=True)
