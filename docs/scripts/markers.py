"""
Renders every marker symbol available
"""

from pathlib import Path

from starplot import MapPlot, Miller
from starplot.styles import MarkerSymbolEnum, PlotStyle, extensions

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "images" / "reference"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

style_medium = PlotStyle().extend(
    extensions.BLUE_MEDIUM,
    extensions.MAP,
    extensions.FIGURE_TRANSPARENT,
)
style_medium.axes.border = None

style_night = PlotStyle().extend(
    extensions.BLUE_NIGHT,
    extensions.MAP,
    extensions.FIGURE_TRANSPARENT,
)

CENTER_RA = 180
CENTER_DEC = 0


marker_styles = {
    "circle": None,
    "circle_cross": None,
    "circle_crosshair": None,
    "circle_line": None,
    "comet": None,
    "diamond": None,
    "ellipse": None,
    "plus": None,
    "satellite": None,
    "square": None,
    "star": None,
    "star_4": None,
    "star_8": None,
    "sun": None,
    "triangle": None,
}


for symbol in MarkerSymbolEnum:
    p = MapPlot(
        projection=Miller(),
        ra_min=CENTER_RA - 10,
        ra_max=CENTER_RA + 10,
        dec_min=CENTER_DEC - 10,
        dec_max=CENTER_DEC + 10,
        style=style_medium,
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
    p.export(str(OUTPUT_DIR / f"marker_{symbol.value}.svg"))
