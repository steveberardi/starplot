from starplot import MapPlot, Projection, _
from starplot.styles import PlotStyle, extensions
from starplot.callables import size_by_magnitude_factory, color_by_bv

style = PlotStyle().extend(
    extensions.GRAYSCALE_DARK,
    extensions.MAP,
)

_sizer = size_by_magnitude_factory(6, 0.02, 7)


def alpha(s):
    if s.magnitude > 9:
        return 0.5
    else:
        return 0.9


p = MapPlot(
    projection=Projection.MOLLWEIDE,
    style=style,
    resolution=4800,
)

p.stars(
    where=[_.magnitude < 11],
    where_labels=[False],
    size_fn=_sizer,
    alpha_fn=alpha,
    color_fn=color_by_bv,
    catalog="big-sky",
    style__marker__edge_color="#c5c5c5",
)
p.stars(
    where=[_.magnitude < 6],
    where_labels=[False],
    size_fn=lambda s: _sizer(s) * 1.5,
    alpha_fn=lambda s: 0.4,
    color_fn=color_by_bv,
    catalog="big-sky",
    style__marker__symbol="star_8",
    style__marker__edge_color=None,
)

p.export("map_milky_way_stars.png", padding=0.1, transparent=True)
