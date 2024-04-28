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
    dec_min=-45.6,
    dec_max=-3,
    style=style,
    resolution=2000,
)
p.constellations()

p.stars(
    where=[Star.magnitude <= 3],  # select the brightest stars
    style__marker__size=76,  # make them bigger
    style__marker__symbol="star_8",  # use an 8-pointed star for bright star markers
    style__marker__zorder=200,
)
p.stars(
    where=[
        Star.magnitude > 3,  # select the dimmer stars
        Star.magnitude < 11,
    ],
    style__marker__size=12,
    bayer_labels=True,
    catalog="tycho-1",
)

p.nebula(
    where=[
        # select DSOs which have no defined magnitude or less than 12
        DSO.magnitude.is_null()
        | (DSO.magnitude < 12),
    ],
    true_size=True,  # plot nebula as their true size
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
p.export("tutorial_06.png", padding=0.08)
