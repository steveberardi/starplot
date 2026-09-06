from starplot import MapPlot, Mercator, _
from starplot.styles import PlotStyle, extensions

style = PlotStyle().extend(
    extensions.BLUE_LIGHT,
    extensions.MAP,
    {
        "legend": {
            "location": "inside_bottom_right",  # show legend inside map
        },
    },
)

p = MapPlot(
    projection=Mercator(),  # specify a non-perspective projection
    ra_min=3.6 * 15,  # limit the map to a specific area
    ra_max=7.8 * 15,
    dec_min=-15,
    dec_max=27,
    style=style,
    resolution=1200,
    autoscale=True,  # automatically adjust the scale based on the resolution
)

p.gridlines()  # add gridlines
p.constellations()
p.constellation_borders()

p.stars(
    where=[_.magnitude < 6.4],
    where_labels=[_.magnitude < 4],
    bayer_labels=True,
    flamsteed_labels=True,
)  # include Bayer and Flamsteed labels with the stars

p.nebula(
    where=[(_.magnitude < 6.4) | (_.magnitude.isnull())],
    where_true_size=[_.size > 0.5],
)
p.open_clusters(
    where=[(_.magnitude < 6.4) | (_.magnitude.isnull())],
    where_true_size=[_.size > 0.5],
)

p.milky_way()
p.ecliptic()

p.legend()  # add a legend

p.constellation_labels()  # Plot the constellation labels last for best placement

p.export("tutorial_04.svg")
