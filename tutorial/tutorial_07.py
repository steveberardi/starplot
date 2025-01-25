from datetime import datetime

from pytz import timezone

from starplot import Planet, optics
from starplot.styles import PlotStyle, extensions

tonight = datetime.now(timezone("America/Los_Angeles")).replace(hour=21)

# get Jupiter for tonight
jupiter = Planet.get("jupiter", tonight)

# create an optic plot directly from Jupiter instance
p = jupiter.create_optic(
    lat=32.97,
    lon=-117.038611,
    dt=tonight,
    optic=optics.Refractor(
        focal_length=600,
        eyepiece_focal_length=4,
        eyepiece_fov=52,
    ),
    style=PlotStyle().extend(extensions.GRAYSCALE_DARK),
    raise_on_below_horizon=False,
    autoscale=True,
)
p.planets(
    true_size=True,
    # since we're plotting the planets as their "true size"
    # the 'auto' offset won't work (it's not supported yet!)
    # so we manually set the offsets here:
    style__label__offset_x=86,
    style__label__offset_y=-40,
    style__label__font_size=56,
    style__marker__color="#fcdb72",
)
p.export("tutorial_07.png", padding=0)
