from starplot import MapPlot, Miller, callables, _
from starplot.styles import PlotStyle, extensions

style = PlotStyle().extend(
    extensions.BLUE_NIGHT,
    extensions.MAP,
)
p = MapPlot(
    projection=Miller(),
    ra_min=15 * 15,
    ra_max=20 * 15,
    dec_min=-45.2,
    dec_max=-3,
    style=style,
    resolution=3600,
    scale=0.8,
)
p.constellations()
p.constellation_borders()

p.stars(
    # select the brightest stars:
    where=[_.magnitude <= 3],
    # here we make the stars 2x bigger by passing in a custom size function (i.e. a callable)
    # you'll learn more about this later in the tutorial...
    size_fn=lambda d: callables.size_by_magnitude(d) * 2,
    # use an 8-pointed star for bright star markers:
    style__marker__symbol="star_8",
    style__label__offset_x=8,
    style__label__offset_y=-8,
    style__label__border_width=2,
)
p.stars(
    where=[
        _.magnitude > 3,  # select the dimmer stars
        _.magnitude < 8,
    ],
    bayer_labels=True,
)

p.nebula(
    # select DSOs which have no defined magnitude or less than 7
    where=[_.magnitude.isnull() | (_.magnitude < 7)],
    true_size=True,  # plot nebula as their true size
)
p.open_clusters(
    where=[_.magnitude.isnull() | (_.magnitude < 7)],
    true_size=False,
)
p.globular_clusters(
    where=[_.magnitude.isnull() | (_.magnitude < 7)],
    true_size=False,
)

p.ecliptic()
p.milky_way()
p.constellation_labels()

p.export("tutorial_06.png", padding=0.08)
