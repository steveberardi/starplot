from starplot import MapPlot, Projection, DSO, Star
from starplot.styles import PlotStyle, extensions

style = PlotStyle().extend(
    extensions.ANTIQUE,
    extensions.MAP,
    {
        "bayer_labels": {
            "font_name": "GFS Didot",
            "font_size": 7,
        },
    },
)
p = MapPlot(
    projection=Projection.MILLER,
    ra_min=15.6,
    ra_max=19.8,
    dec_min=-54,
    dec_max=-8,
    style=style,
    resolution=2800,
)
p.constellations()

p.stars(
    where=[Star.magnitude <= 3],
    style__marker__size=72,
    style__marker__symbol="star_8",
)
p.stars(
    where=[
        Star.magnitude > 3,
        Star.magnitude < 12,
    ],
    style__marker__size=12,
    bayer_labels=True,
    catalog="tycho-1",
)

p.dsos(where=[DSO.magnitude.is_null() | (DSO.magnitude < 12)], true_size=True)

p.constellation_borders()
p.ecliptic()
p.celestial_equator()
p.milky_way()
p.gridlines(tick_marks=True)
p.export("map_sagittarius.png", padding=0.2)
