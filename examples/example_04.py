from starplot import MapPlot, Projection
from starplot.styles import PlotStyle, extensions

style = PlotStyle().extend(
    extensions.GRAYSCALE_DARK,
    extensions.MAP,
    {
        "bayer_labels": {
            "font_name": "GFS Didot",
            "font_size": 7,
        }
    },
)
p = MapPlot(
    projection=Projection.STEREO_SOUTH,
    ra_min=17,
    ra_max=19.5,
    dec_min=-46,
    dec_max=-14,
    style=style,
    resolution=3200,
)
p.constellations()
p.stars(mag=13, bayer_labels=True)
p.dsos(mag=13, true_size=True, labels=None)
p.constellation_borders()
p.ecliptic()
p.celestial_equator()
p.milky_way()
p.gridlines()
p.export("04_map_sagittarius.png", padding=0.2)
