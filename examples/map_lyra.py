from starplot import MapPlot, Projection, Constellation
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
        "background_color": "#d6d6d6",
    },
)
lyra = Constellation.get(name="Lyra")
p = MapPlot(
    projection=Projection.STEREO_NORTH,
    ra_min=17,
    ra_max=20.6,
    dec_min=18,
    dec_max=54,
    style=style,
    resolution=3000,
)
p.stars(mag=9, bayer_labels=True)
p.dsos(mag=9, labels=None)
p.constellations()
p.constellation_borders()
p.milky_way()
p.ecliptic()

points = list(zip(*lyra.boundary.exterior.coords.xy))
p.polygon(
    points,
    style__fill_color="#fff",
    style__zorder=-2000,
    style__edge_width=1,
    style__edge_color="#000",
    style__line_style="dashed",
)

p.export("map_lyra.png", padding=0.3, transparent=True)
