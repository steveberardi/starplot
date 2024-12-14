from starplot import MapPlot, Projection, Star
from starplot.styles import PlotStyle, extensions

style = PlotStyle().extend(
    extensions.BLUE_DARK,
    extensions.MAP,
)

p = MapPlot(
    projection=Projection.STEREO_NORTH,
    ra_min=10.75,
    ra_max=14.2,
    dec_min=47,
    dec_max=65,
    style=style,
    resolution=1800,
)
p.stars(
    where=[
        Star.magnitude < 3.6,
        Star.dec > 45,
        Star.dec < 64,
    ],
    style__marker__symbol="star",
    style__marker__color="#ffff73",
    style__label__font_size=20,
    style__label__font_weight="normal",
)
p.export("map_big_dipper.png", transparent=True)
