from datetime import datetime
from zoneinfo import ZoneInfo

from starplot import Observer, Star, Binoculars, styles, callables, _

tz = ZoneInfo("America/Los_Angeles")
tonight = datetime.now(tz).replace(hour=21)

observer = Observer(
    dt=tonight,
    lat=32.97,
    lon=-117.038611,
)

style = styles.PlotStyle().extend(
    styles.extensions.GRAYSCALE_DARK,
    styles.extensions.OPTIC,
)

antares = Star.get(name="Antares")

p = antares.create_optic(
    observer=observer,
    optic=Binoculars(
        magnification=10,
        fov=65,
    ),
    style=style,
    raise_on_below_horizon=False,
    autoscale=True,
)

p.stars(
    where=[_.magnitude < 12],
    where_labels=[_.magnitude < 8],
    bayer_labels=True,
    color_fn=callables.color_by_bv,  # <-- here's where we specify the callable
)

p.export("tutorial_08.png", padding=0)
