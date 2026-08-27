"""
Renders every marker symbol available
"""

from pathlib import Path

from starplot import MapPlot, Miller
from starplot.styles import MarkerSymbolEnum, PlotStyle, extensions, MarkerStyle, ObjectStyle

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "images" / "reference"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

style_medium = PlotStyle().extend(
    extensions.BLUE_MEDIUM,
    extensions.MAP,
    extensions.FIGURE_TRANSPARENT,
)
style_medium.axes.border = None
style_medium.axes.background.fill = None

style_night = PlotStyle().extend(
    extensions.BLUE_NIGHT,
    extensions.MAP,
    extensions.FIGURE_TRANSPARENT,
)

CENTER_RA = 180
CENTER_DEC = 0

default_style = MarkerStyle(
        fill="#c6e4f9",
        stroke="#053659",
        stroke_width=2,
    )

marker_styles = {
    "circle": style_medium.dso_open_cluster.marker,
    "circle_cross": style_medium.dso_globular_cluster.marker,
    "circle_crosshair": style_medium.dso_nebula.marker,
    "circle_line": style_medium.dso_double_star.marker,
    "comet": default_style,
    "diamond": default_style,
    "ellipse": style_medium.dso_galaxy.marker,
    "plus": default_style,
    "satellite": default_style,
    "square": style_medium.dso_nebula.marker,
    "star": default_style,
    "star_4": default_style,
    "star_8": default_style,
    "triangle": default_style,
}


for symbol in MarkerSymbolEnum:
    symbol_str = symbol.value

    marker_style = marker_styles.get(symbol_str)
    marker_style.size = 60
    marker_style.symbol = symbol_str
    marker_style.stroke_width = default_style.stroke_width


    object_style = ObjectStyle(marker=marker_style)

    p = MapPlot(
        projection=Miller(),
        ra_min=CENTER_RA - 10,
        ra_max=CENTER_RA + 10,
        dec_min=CENTER_DEC - 10,
        dec_max=CENTER_DEC + 10,
        style=style_medium,
        resolution=64 if symbol_str != "circle_line" else 128,
        scale=0.5,
    )
    p.marker(
        ra=CENTER_RA,
        dec=CENTER_DEC,
        style=object_style,
    )
    p.export(str(OUTPUT_DIR / f"marker_{symbol.value}.svg"))
