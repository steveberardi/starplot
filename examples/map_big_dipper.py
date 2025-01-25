from starplot import MapPlot, Projection, _
from starplot.styles import PlotStyle, extensions

style = PlotStyle().extend(
    extensions.BLUE_DARK,
    extensions.MAP,
)

p = MapPlot(
    projection=Projection.STEREO_NORTH,
    ra_min=10.75 * 15,
    ra_max=14.2 * 15,
    dec_min=47,
    dec_max=65,
    style=style,
    resolution=1800,
)
p.stars(
    where=[
        _.magnitude < 3.6,
        _.dec > 45,
        _.dec < 64,
    ],
    style__marker__symbol="star",
    style__marker__color="#ffff73",
    style__label__font_size=20,
    style__label__font_weight="normal",
)
p.export("map_big_dipper.png", transparent=True)
