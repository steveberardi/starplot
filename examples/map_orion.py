from starplot import MapPlot, Projection, Star
from starplot.styles import PlotStyle, PolygonStyle, extensions

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
p.stars(
    mag=9, bayer_labels=True, flamsteed_labels=True, where_labels=[Star.magnitude < 9]
)
p.open_clusters(mag=9, labels=None, label_fn=lambda d: d.ngc)
p.nebula(mag=9, labels=None, label_fn=lambda d: d.ngc)
p.constellations()
p.constellation_borders()
p.milky_way()
p.ecliptic()
p.legend()

p.export("map_orion.png", padding=0.3, transparent=True)
