from starplot import MapPlot, StereoNorth, _
from starplot.styles import PlotStyle, extensions

style = PlotStyle().extend(
    extensions.BLUE_DARK,
    extensions.MAP,
    {
        "axes": {
            "background_color": "#174567",
        }
    },
)

p = MapPlot(
    projection=StereoNorth(),
    ra_min=10.75 * 15,
    ra_max=14.2 * 15,
    dec_min=47,
    dec_max=65,
    style=style,
    resolution=2000,
)
p.stars(
    where=[
        _.magnitude < 3.6,
        _.dec > 45,
        _.dec < 64,
    ],
    size_fn=lambda s: 58,  # make stars a constant size
    style__marker__symbol="star",
    style__marker__color="hsl(59, 100%, 51%)",
    style__label__font_size=16,
    style__label__font_weight=500,
)
p.export("map_big_dipper.png")
