from starplot import MapPlot, Equidistant, geometry, _
from starplot.styles import PlotStyle, extensions

style = PlotStyle().extend(
    extensions.BLUE_MEDIUM,
    # extensions.BLUE_NIGHT,
    # extensions.GRAYSCALE,
    # extensions.STARPLOT,
    extensions.MAP,
    extensions.FIGURE_TRANSPARENT,
)


p = MapPlot(
    projection=Equidistant(center_dec=90),
    dec_min=30,
    style=style,
    resolution=4000,
    scale=0.8,
    clip_path=geometry.circle(
        center=(0,90),
        diameter_degrees=150,
        num_pts=500,
    )
)
p.gridlines(labels=False)
p.constellations()
p.constellation_borders()

p.stars(
    where=[_.magnitude < 7], 
    # bayer_labels=True,
    # flamsteed_labels=True,
    where_labels=[False]
)
p.open_clusters(
    where=[_.magnitude < 12],
    where_labels=[False],
    where_true_size=[False],
)
p.galaxies(
    where=[_.magnitude < 12],
    where_labels=[False],
    where_true_size=[False],
)
p.nebula(
    where=[_.magnitude < 12],
    where_labels=[False],
    where_true_size=[False],
)

p.constellation_labels()
p.ecliptic()
p.milky_way()

p.export("map_equidistant.png")
