from starplot import MapPlot, Miller, _
from starplot.styles import PlotStyle, extensions


style = PlotStyle().extend(
    extensions.BLUE_DARK,
    extensions.MAP,
)

p = MapPlot(
    projection=Miller(),
    ra_min=0,
    ra_max=360,
    dec_min=-80,
    dec_max=80,
    style=style,
    resolution=6000,
    # since this map has a very large extent, let's scale everything down
    scale=0.8,
)
p.gridlines()
p.constellations()
p.stars(where=[_.magnitude < 6], where_labels=[_.magnitude < 2.1])
p.open_clusters(
    where=[
        _.magnitude <= 8,
    ],
    where_labels=[False],
    true_size=False,
)
p.globular_clusters(
    where=[
        _.magnitude <= 9,
    ],
    where_labels=[False],
    true_size=False,
)
p.galaxies(
    where=[
        _.magnitude <= 10,
    ],
    where_labels=[False],
    true_size=False,
)
p.nebula(
    where=[(_.magnitude <= 10) | (_.magnitude.isnull()), _.size > 0.05],
    where_labels=[False],
)

p.constellation_labels(style__font_size=28)
p.milky_way()
p.ecliptic()
p.celestial_equator()

p.export("map_big.png", padding=0.5)
