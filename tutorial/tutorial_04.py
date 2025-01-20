from starplot import MapPlot, Projection, _
from starplot.styles import PlotStyle, extensions

style = PlotStyle().extend(
    extensions.BLUE_LIGHT,
    extensions.MAP,
    {
        "legend": {
            "location": "lower right",  # show legend inside map
            "num_columns": 3,
            "background_alpha": 1,
        },
    },
)

p = MapPlot(
    projection=Projection.MERCATOR,  # specify a non-perspective projection
    ra_min=3.6 * 15,  # limit the map to a specific area
    ra_max=7.8 * 15,
    dec_min=-15,
    dec_max=27,
    style=style,
    resolution=3600,
    autoscale=True,  # automatically adjust the scale based on the resolution
)

p.gridlines()  # add gridlines
p.constellations()
p.constellation_borders()

p.stars(
    where=[_.magnitude < 8], bayer_labels=True, flamsteed_labels=True
)  # include Bayer and Flamsteed labels with the stars


p.nebula(where=[(_.magnitude < 9) | (_.magnitude.isnull())], where_labels=[False])
p.open_clusters(
    where=[(_.magnitude < 9) | (_.magnitude.isnull())], where_labels=[False]
)

p.milky_way()
p.ecliptic()

p.legend()  # add a legend

p.constellation_labels()  # Plot the constellation labels last for best placement

p.export("tutorial_04.png", padding=0.2, transparent=True)
