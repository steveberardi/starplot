from starplot import MapPlot, Projection
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
    projection=Projection.MERCATOR,  # specify a non-perspective projection
    ra_min=3.6,  # limit the map to a specific area
    ra_max=7.8,
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
    mag=8, bayer_labels=True, flamsteed_labels=True
)  # include Bayer and Flamsteed labels with the stars

p.nebula(mag=8, labels=None)
p.open_clusters(mag=8, labels=None)

p.milky_way()
p.ecliptic()

p.legend()  # add a legend

p.constellation_labels()  # Plot the constellation labels last for best placement

p.export("tutorial_04.png", padding=0.2, transparent=True)
