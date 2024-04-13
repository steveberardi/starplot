from starplot import MapPlot, Projection
from starplot.styles import PlotStyle, PolygonStyle, extensions

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
    projection=Projection.MERCATOR,
    ra_min=3.6,
    ra_max=7.8,
    dec_min=-15,
    dec_max=25,
    style=style,
    resolution=3600,
)
p.gridlines()
p.stars(mag=9, bayer_labels=True)
p.dsos(mag=9, labels=None)
p.constellations()
p.constellation_borders()
p.milky_way()
p.ecliptic()

p.ellipse(
    (5.6, -1.2),
    height_degrees=3,
    width_degrees=5,
    style=PolygonStyle(
        fill_color="#ed7eed",
        edge_color="#000",
        alpha=0.2,
    ),
    angle=-22,
)

p.legend()

p.export("map_orion.png", padding=0.5, transparent=True)
