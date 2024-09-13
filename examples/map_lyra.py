from starplot import MapPlot, Projection, Constellation
from starplot.styles import PlotStyle, extensions

style = PlotStyle().extend(
    extensions.BLUE_MEDIUM,
    extensions.MAP,
    {
        "bayer_labels": {
            "font_name": "GFS Didot",  # use a better font for Greek letters
            "font_size": 7,
            "font_alpha": 0.9,
        },
        # "background_color": "#d6d6d6",
    },
)
lyra = Constellation.get(name="Lyra")
p = MapPlot(
    projection=Projection.STEREO_NORTH,
    ra_min=17.8,
    ra_max=20,
    dec_min=19,
    dec_max=53,
    style=style,
    resolution=3000,
    clip_path=lyra.boundary,
)
p.messier(true_size=False, label_fn=lambda d: f"M{d.m}")
p.stars(mag=9, bayer_labels=True)
p.constellations()
p.constellation_borders()
p.milky_way()

points = list(zip(*lyra.boundary.exterior.coords.xy))
p.polygon(
    points,
    style__fill_color="#fff",
    style__zorder=-2000,
)

p.export("map_lyra.png", padding=0.2, transparent=True)
