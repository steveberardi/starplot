from starplot import MapPlot, Projection, DSO, Star
from starplot.styles import PlotStyle, extensions


style = PlotStyle().extend(
    extensions.BLUE_DARK,
    extensions.MAP,
)

p = MapPlot(
    projection=Projection.MILLER,
    ra_min=0,
    ra_max=24,
    dec_min=-80,
    dec_max=80,
    style=style,
    resolution=6000,
    # since this map has a very large extent, let's scale everything down
    scale=0.8,
)
p.gridlines()
p.constellations()
p.stars(mag=6, where_labels=[Star.magnitude < 2.1])
p.open_clusters(
    labels=None,
    where=[
        DSO.magnitude <= 8,
    ],
    true_size=False,
)
p.globular_clusters(
    labels=None,
    where=[
        DSO.magnitude <= 9,
    ],
    true_size=False,
)
p.galaxies(
    labels=None,
    where=[
        DSO.magnitude <= 10,
    ],
    true_size=False,
)
p.nebula(
    labels=None,
    where=[(DSO.magnitude <= 10) | (DSO.magnitude.is_null()), DSO.size > 0.05],
)

p.constellation_labels(style__font_size=28)
p.milky_way()
p.ecliptic()
p.celestial_equator()

p.export("map_big.png", padding=0.5)
