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
        "dso_open_cluster": {
            "marker": {
                "size": 17,
            },
        },
    },
)
p = MapPlot(
    projection=Projection.MILLER,
    ra_min=15.6,
    ra_max=19.8,
    dec_min=-51.6,
    dec_max=-3,
    style=style,
    resolution=3000,
)
p.constellations()

p.stars(
    where=[Star.magnitude <= 3],
    style__marker__size=72,
    style__marker__symbol="star_8",
    style__marker__zorder=200,
)
p.stars(
    where=[
        Star.magnitude > 3,
        Star.magnitude < 11,
    ],
    style__marker__size=12,
    bayer_labels=True,
    catalog="tycho-1",
)

p.nebula(
    where=[
        DSO.magnitude.is_null() | (DSO.magnitude < 12),
    ],
    true_size=True,
)
p.open_clusters(
    where=[
        DSO.magnitude.is_null() | (DSO.magnitude < 12),
    ],
    true_size=False,
)
p.constellation_borders()
p.ecliptic()
p.celestial_equator()
p.milky_way()
p.export("map_sagittarius.png", padding=0.08)
