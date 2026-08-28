from starplot import MapPlot, StereoNorth, _, Constellation
from starplot.styles import PlotStyle, extensions

style = PlotStyle().extend(
    extensions.BLUE_NIGHT,
    extensions.MAP,
)

# define your gradient
style.axes.background.fill = [
    (0.0, "#f4d58d"),
    (0.3, "#c17ecb"),
    (0.7, "#4b3f8f"),
    (1.0, "#100d29"),  # last stop should always be 1.0
]

cas = Constellation.get(iau_id="cas")

p = MapPlot(
    projection=StereoNorth(center_ra=15),
    ra_min=-5,
    ra_max=35,
    dec_min=55,
    dec_max=65,
    style=style,
    scale=1.5,
)
p.stars(
    where=[_.hip.isin(cas.star_hip_ids)],
    where_labels=False,
    style__marker__symbol="star_4",
    style__marker__stroke_width=4,
    size_fn=lambda s: 80,
)
p.constellations()
p.export("gradient.svg")
