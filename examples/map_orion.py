from starplot import MapPlot, Miller, _
from starplot.styles import PlotStyle, extensions

style = PlotStyle().extend(
    extensions.BLUE_LIGHT,
    extensions.MAP,
)

p = MapPlot(
    projection=Miller(),
    ra_min=3.6 * 15,
    ra_max=7.8 * 15,
    dec_min=-15,
    dec_max=25,
    style=style,
    resolution=4096,
    autoscale=True,
)
p.gridlines()
p.constellations()
p.constellation_borders()

p.stars(where=[_.magnitude < 8], bayer_labels=True, where_labels=[_.magnitude < 5])

p.open_clusters(
    where=[_.size < 1, _.magnitude < 9],
    where_labels=[False],
    true_size=False,
)
p.open_clusters(
    # plot larger clusters as their true apparent size
    where=[_.size > 1, (_.magnitude < 9) | (_.magnitude.isnull())],
    where_labels=[False],
)

p.nebula(
    where=[(_.magnitude < 9) | (_.magnitude.isnull())],
)

p.constellation_labels()
p.milky_way()
p.ecliptic()

p.export("map_orion.png", padding=0.3, transparent=True)
