from starplot import MapPlot, Projection
from starplot.styles import PlotStyle, extensions, MarkerSymbolEnum

style = PlotStyle().extend(
    extensions.MINIMAL,
    extensions.GRAYSCALE,
    extensions.MAP,
)

style.star.marker.symbol = MarkerSymbolEnum.STAR

# Star sizes are calculated based on their magnitude first,
# but then that result will be multiplied by the star's marker size in the PlotStyle
# so, adjusting the star marker size is a way to make all stars bigger or smaller
style.star.marker.size = 50

p = MapPlot(
    projection=Projection.STEREO_NORTH,
    ra_min=10.8,
    ra_max=14,
    dec_min=48,
    dec_max=64,
    limiting_magnitude=3.6,
    style=style,
    resolution=1400,
    dso_types=[],  # this is one way to hide all deep sky objects
)

p.export("06_big_dipper_stars.png", padding=0.2)
