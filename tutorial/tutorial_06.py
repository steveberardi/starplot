from starplot import MapPlot, Projection, DSO, Star, callables
from starplot.styles import PlotStyle, extensions

style = PlotStyle().extend(
    extensions.ANTIQUE,
    extensions.MAP,
)
p = MapPlot(
    projection=Projection.MILLER,
    ra_min=15.6,
    ra_max=19.8,
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
    where=[Star.magnitude <= 3],
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
        Star.magnitude > 3,  # select the dimmer stars
        Star.magnitude < 9,
    ],
    bayer_labels=True,
    catalog="big-sky-mag11",
)

p.nebula(
    where=[
        # select DSOs which have no defined magnitude or less than 10
        DSO.magnitude.is_null()
        | (DSO.magnitude < 10),
    ],
    true_size=True,  # plot nebula as their true size
)
p.open_clusters(
    where=[
        DSO.magnitude.is_null() | (DSO.magnitude < 10),
    ],
    true_size=False,
)
p.globular_clusters(
    where=[
        DSO.magnitude.is_null() | (DSO.magnitude < 10),
    ],
    true_size=False,
)

p.ecliptic()
p.celestial_equator()
p.milky_way()
p.export("tutorial_06.png", padding=0.08)
