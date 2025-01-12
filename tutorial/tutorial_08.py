from datetime import datetime

from pytz import timezone

from starplot import Star, optics, styles, callables, _

tonight = datetime.now(timezone("America/Los_Angeles")).replace(hour=21)

style = styles.PlotStyle().extend(
    styles.extensions.GRAYSCALE_DARK,
    styles.extensions.OPTIC,
)

antares = Star.get(name="Antares")

p = antares.create_optic(
    lat=32.97,
    lon=-117.038611,
    dt=tonight,
    optic=optics.Binoculars(
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
