from datetime import datetime

from pytz import timezone

from starplot.styles import PlotStyle, extensions
from starplot import Planet, optics

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
)
p.planets(
    true_size=True,
    style__label__offset_x=64,
    style__label__offset_y=-20,
    style__label__font_size=26,
    style__marker__color="#fcdb72",
)
p.export("tutorial_07.png", padding=0)
