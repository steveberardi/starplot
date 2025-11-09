from starplot import MapPlot, LambertAzEqArea, _
from starplot.styles import PlotStyle, extensions


style = PlotStyle().extend(
    extensions.BLUE_MEDIUM,
    extensions.MAP,
)
p = MapPlot(
    projection=LambertAzEqArea(center_ra=0.5 * 15, center_dec=90),
    ra_min=23.21 * 15,
    ra_max=26.6 * 15,
    dec_min=49.5,
    dec_max=68,
    style=style,
    resolution=4000 * 1,
    scale=1.2,
)
p.constellations(where=[_.iau_id == "cas"])  # only plot the lines of Cassiopeia

p.stars(
    where=[
        _.magnitude < 9,
    ],
    bayer_labels=True,
    flamsteed_labels=True,
)

p.nebula(
    where=[
        (_.magnitude.isnull()) | (_.magnitude < 8),
    ],
    true_size=True,
)
p.open_clusters(
    where=[
        (_.magnitude.isnull()) | (_.magnitude < 8),
    ],
    true_size=False,
)

p.constellation_labels()

p.gridlines(
    dec_locations=[d for d in range(0, 90, 5)],
)

p.export("map_cas.png", padding=0.5)
