from starplot import MapPlot, Projection
from starplot.models import DSO
from starplot.styles import PlotStyle, extensions


style = PlotStyle().extend(
    extensions.BLUE_DARK,
    extensions.MAP,
)

style.star.label.font_size = 4
style.constellation.label.font_size = 6
style.constellation.line.width = 2

p = MapPlot(
    projection=Projection.MILLER,
    ra_min=0,
    ra_max=24,
    dec_min=-80,
    dec_max=80,
    style=style,
    resolution=6000,
)
p.stars(mag=8)
p.dsos(
    labels=None,
    where=[
        DSO.magnitude <= 8,
        DSO.size > 0.05,
    ],
)
p.gridlines()
p.milky_way()
p.ecliptic(style={"line": {"style": "dashed"}})
p.celestial_equator()

p.export("map_big.png", padding=0.5)
