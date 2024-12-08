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
    where=[Star.magnitude <= 3],
    size_fn=lambda d: callables.size_by_magnitude(d) * 2,  # make them 2x bigger
    style__marker__symbol="star_8",
    style__label__offset_x=8,
    style__label__offset_y=-8,
    style__label__border_width=2,
    style__label__border_color="#fefaed",
)
p.stars(
    where=[
        Star.magnitude > 3,
        Star.magnitude < 9,
    ],
    bayer_labels=True,
    flamsteed_labels=True,
    catalog="big-sky-mag11",
)

p.nebula(
    where=[
        DSO.magnitude.is_null() | (DSO.magnitude < 12),
    ],
    true_size=True,
    label_fn=lambda d: d.ic,
)
p.open_clusters(
    where=[
        DSO.magnitude.is_null() | (DSO.magnitude < 12),
    ],
    true_size=False,
    label_fn=lambda d: d.ngc,
)
p.globular_clusters(
    where=[
        DSO.magnitude.is_null() | (DSO.magnitude < 12),
    ],
    true_size=False,
    label_fn=lambda d: d.ngc,
)
p.ecliptic()
p.celestial_equator()
p.milky_way()
p.export("map_sagittarius.png", padding=0.08)
