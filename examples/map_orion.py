from starplot import MapPlot, Projection, Star, DSO
from starplot.styles import PlotStyle, extensions

style = PlotStyle().extend(
    extensions.BLUE_LIGHT,
    extensions.MAP,
    {
        "legend": {
            "location": "lower right",  # show legend inside map
            "num_columns": 1,
            "background_alpha": 1,
        },
    },
)

p = MapPlot(
    projection=Projection.MERCATOR,
    ra_min=3.6,
    ra_max=7.8,
    dec_min=-15,
    dec_max=25,
    style=style,
    resolution=3600,
    autoscale=True,
)
p.gridlines()
p.constellations()
p.constellation_borders()

p.stars(mag=8, bayer_labels=True, where_labels=[Star.magnitude < 5])

p.open_clusters(
    where=[DSO.size < 1, DSO.magnitude < 9],
    labels=None,
    label_fn=lambda d: d.ngc,
    true_size=False,
)
p.open_clusters(
    # plot larger clusters as their true apparent size
    where=[DSO.size > 1, (DSO.magnitude < 9) | (DSO.magnitude.is_null())],
    labels=None,
)

p.nebula(mag=9, labels=None, label_fn=lambda d: d.ngc)

p.constellation_labels()
p.milky_way()
p.ecliptic()
p.legend()

p.export("map_orion.png", padding=0.3, transparent=True)
