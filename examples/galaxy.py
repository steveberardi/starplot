from starplot import _, GalaxyPlot, DSO
from starplot.styles import PlotStyle, extensions


style = PlotStyle().extend(
    extensions.BLUE_NIGHT,
    extensions.MAP,
    extensions.FIGURE_TRANSPARENT,
)

p = GalaxyPlot(
    style=style,
    resolution=2000,
    scale=0.4,
)
p.gridlines()

p.galactic_equator(num_labels=2)
p.celestial_equator(num_labels=2)
p.ecliptic(num_labels=2)

p.milky_way()

p.stars(
    where=[_.magnitude < 7],
    where_labels=[False],
    size_fn=lambda star: 8 - star.magnitude,
    style__marker__edge_color="#c5c5c5",
)

p.open_clusters(
    where=[(_.magnitude < 16) | (_.magnitude.isnull())],
    where_labels=[False],
    where_true_size=[False],
)

p.export("galaxy.png")
