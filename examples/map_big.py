from starplot import MapPlot, Projection, DSO, Star
from starplot.styles import PlotStyle, extensions


style = PlotStyle().extend(
    extensions.BLUE_DARK,
    extensions.MAP,
)

p = MapPlot(
    projection=Projection.MILLER,
    ra_min=0,
    ra_max=24,
    dec_min=-80,
    dec_max=80,
    style=style,
    resolution=6000,
    scale=0.8,
)
p.stars(mag=6, where_labels=[Star.magnitude < 2.1])
p.dsos(
    labels=None,
    where=[
        DSO.magnitude <= 6,
        DSO.size > 0.05,
    ],
)
p.gridlines()
p.milky_way()
p.ecliptic(style={"line": {"style": "dashed"}})
p.celestial_equator()

p.export("map_big.png", padding=0.5)
