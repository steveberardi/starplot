"""
Renders every marker symbol available
"""

from starplot import MapPlot, Miller
from starplot.styles import MarkerSymbolEnum, PlotStyle, extensions

style = PlotStyle().extend(
    extensions.STARPLOT,
    extensions.MAP,
    extensions.FIGURE_TRANSPARENT,
)
style.axes.border = None

CENTER_RA = 180
CENTER_DEC = 0

for symbol in MarkerSymbolEnum:
    p = MapPlot(
        projection=Miller(),
        ra_min=CENTER_RA - 10,
        ra_max=CENTER_RA + 10,
        dec_min=CENTER_DEC - 10,
        dec_max=CENTER_DEC + 10,
        style=style,
        resolution=300,
    )
    p.marker(
        ra=CENTER_RA,
        dec=CENTER_DEC,
        style__marker__symbol=symbol.value,
        style__marker__size=150,
        style__marker__fill="hsl(205, 83%, 16%)",
        style__marker__stroke="hsl(205, 83%, 16%)",
        style__marker__stroke_width=8,
    )
    p.export(f"marker_{symbol.value}.svg")
