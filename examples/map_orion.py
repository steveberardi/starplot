from starplot import MapPlot, Projection, _
from starplot.styles import PlotStyle, extensions

style = PlotStyle().extend(
    extensions.BLUE_LIGHT,
    extensions.MAP,
)

p = MapPlot(
    projection=Projection.MERCATOR,
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
    labels=None,
    label_fn=lambda d: d.ngc,
    true_size=False,
)
p.open_clusters(
    # plot larger clusters as their true apparent size
    where=[_.size > 1, (_.magnitude < 9) | (_.magnitude.isnull())],
    labels=None,
)

p.nebula(
    where=[(_.magnitude < 9) | (_.magnitude.isnull())],
    labels=None,
    label_fn=lambda d: d.ngc,
)

p.constellation_labels()
p.milky_way()
p.ecliptic()

p.export("map_orion.png", padding=0.3, transparent=True)
