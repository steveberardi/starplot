from starplot import MapPlot, Projection
from starplot.styles import PlotStyle, extensions

style = PlotStyle().extend(
    extensions.BLUE_LIGHT,
    extensions.MAP,
    {
        "bayer_labels": {
            "font_name": "GFS Didot",  # use a better font for Greek letters
            "font_size": 7,
            "font_alpha": 0.9,
        },
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
)

p.gridlines()  # add gridlines

p.stars(mag=9, bayer_labels=True)  # include bayer labels with the stars

p.dsos(mag=9, labels=None)
p.constellations()
p.constellation_borders()
p.milky_way()
p.ecliptic()

p.legend()  # add a legend

p.export("tutorial_04.png", padding=0.2, transparent=True)
