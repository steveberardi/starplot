from starplot import MapPlot, Projection, callables, _
from starplot.styles import PlotStyle, extensions

style = PlotStyle().extend(
    extensions.ANTIQUE,
    extensions.MAP,
)
p = MapPlot(
    projection=Projection.MILLER,
    ra_min=15.6 * 15,
    ra_max=19.8 * 15,
    dec_min=-45.2,
    dec_max=-3,
    style=style,
    resolution=4000,
    autoscale=True,
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
    style__label__border_color="#fefaed",
)
p.stars(
    where=[
        _.magnitude > 3,  # select the dimmer stars
        _.magnitude < 9,
    ],
    bayer_labels=True,
    catalog="big-sky-mag11",
)

p.nebula(
    where=[
        # select DSOs which have no defined magnitude or less than 10
        _.magnitude.isnull()
        | (_.magnitude < 10),
    ],
    true_size=True,  # plot nebula as their true size
)
p.open_clusters(
    where=[
        _.magnitude.isnull() | (_.magnitude < 10),
    ],
    true_size=False,
)
p.globular_clusters(
    where=[
        _.magnitude.isnull() | (_.magnitude < 10),
    ],
    true_size=False,
)

p.ecliptic()
p.milky_way()
p.constellation_labels()

p.export("tutorial_06.png", padding=0.08)
