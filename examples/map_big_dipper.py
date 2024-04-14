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
    # By default, star sizes are calculated based on their magnitude first,
    # but then that result will be multiplied by the star's marker size in the PlotStyle
    # so, adjusting the star marker size is a way to make all stars bigger or smaller
    style__marker__size=96,
    style__marker__symbol="star",
    style__marker__color="#ffff73",
    style__label__font_size=13,
    style__label__font_weight="normal",
    style__label__anchor_point="bottom right",
    style__label__offset_x=16,
    style__label__offset_y=-52,
)
p.export("map_big_dipper.png", transparent=True)
