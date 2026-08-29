from typing import Literal

from pydantic import Field, field_serializer, field_validator

from starplot.styles.base import BaseStyle
from starplot.styles.constants import (
    DashArray,
    FontWeight,
    GradientType,
    ZOrder,
)
from starplot.styles.types import Color, MarkerSymbol, _validate_stops

_DASH_ARRAY_VALUES = {
    DashArray.SOLID: None,
    DashArray.DASHED: (12, 6),
    DashArray.DOTTED: (0, 5),
    DashArray.DASHED_DOTS: (10, 2, 10),
}


def _dash_array_attrs(
    dash_array: Literal["solid", "dashed", "dashdot", "dotted"] | tuple | None,
    scale: float,
    nominal: float = 100,
) -> dict:
    """
    Resolves a `dash_array` field (a DashArray value, raw tuple, or None) into
    `stroke-dasharray`/`pathLength` SVG attrs.

    The dasharray values are scaled like everything else drawn on the plot,
    and the pattern is normalized via `pathLength` so it repeats a whole
    number of times from one end of the path to the other -- without this,
    the last repeat gets cut off part way through a dash/gap wherever the
    path happens to end, which is most noticeable on short paths where the
    pattern only repeats once or twice. `pathLength` is chosen as the
    nearest multiple of one full dash/gap cycle to `nominal`, so the
    pattern's visual density stays close to what plain (unnormalized)
    values would look like.
    """
    if not dash_array:
        return {}

    values = (
        _DASH_ARRAY_VALUES.get(dash_array)
        if isinstance(dash_array, str)
        else dash_array
    )
    if not values:
        return {}

    scaled = [n * scale for n in values]
    cycle = sum(scaled)
    if cycle <= 0:
        return {}

    # TODO : find workaround for plotting balanced dash patterns
    # "pathLength": round(path_length, 4), # not supported in cairo-svg
    # repeats = max(1, round(nominal / cycle))
    # path_length = cycle * repeats

    return {
        "stroke-dasharray": ",".join(str(round(n, 4)) for n in scaled),
    }


class GradientStyle(BaseStyle):
    """
    Styling properties for a gradient fill.
    """

    stops: tuple[tuple[float, Color], ...]
    """
    The gradient's color stops, as a tuple of `(offset, color)` pairs. The last stop's offset must always be `1.0`. 
    
    Example:

    ```
    (
        (0.0, "#7abfff"),
        (0.2, "#7abfff"),
        (0.9, "#568feb"),
        (1.0, "#3f7ee3"),
    )
    ```
    """

    type: Literal["linear", "radial"] = GradientType.RADIAL
    """Type / direction of the gradient."""

    @field_validator("stops")
    @classmethod
    def _check_stops(cls, stops):
        return _validate_stops(stops)

    @field_serializer("stops")
    def _serialize_stops(self, stops):
        return [(offset, c.as_hex() if c else None) for offset, c in stops]


class MarkerStyle(BaseStyle):
    """Styling properties for markers."""

    fill: Color | GradientStyle | None = Color("#000")
    """
    Fill color of the marker

    This can be a single color (e.g. `#7abfff`) or a `GradientStyle` that defines a gradient. For example:

    ```
    GradientStyle(
        stops=(
            (0.0, "#7abfff"),
            (0.2, "#7abfff"),
            (0.9, "#568feb"),
            (1.0, "#3f7ee3"),  # the last stop should always be at 1.0
        ),
    )
    ```

    There are a few predefined gradients available as [style extensions](/reference-styling/#style-extensions).

    """

    stroke: Color | None = Color("#000")
    """Stroke color of marker. Can be a hex, rgb, hsl, or word string."""

    stroke_width: float = 1
    """Stroke width of marker, in pixels."""

    dash_array: (
        Literal["solid", "dashed", "dashdot", "dotted"] | tuple[int, ...] | None
    ) = None
    """Dash style of the marker's stroke. Can be a predefined value in `DashArray` or a tuple [stroke dasharray](https://css-tricks.com/almanac/properties/s/stroke-dasharray/). A dash of `0` (e.g. `(0, 5)`) draws a row of evenly-spaced round dots instead of dashes -- pair it with `dash_capstyle=CapStyle.ROUND`, since a zero-length dash is only visible with a round cap."""

    dash_capstyle: Literal["square", "butt", "round"] = "square"
    """Style of dash endpoints"""

    symbol: Literal[
        "plus",
        "circle",
        "square",
        "star",
        "diamond",
        "triangle",
        "circle_cross",
        "circle_crosshair",
        "circle_line",
        "comet",
        "star_4",
        "star_8",
        "ellipse",
        "satellite",
    ] = "circle"
    """Symbol for marker."""

    size: float = 24
    """Size of marker in pixels"""

    opacity: float = Field(default=1.0, ge=0, le=1)
    """Opacity (transparency) of the marker (0 to 1)"""

    zorder: int = ZOrder.LAYER_2
    """Zorder of marker"""

    def css(self, scale: float = 1) -> dict:
        solid_fill = self.fill is not None and not isinstance(self.fill, GradientStyle)
        attrs = {
            "fill": self.fill.as_hex() if solid_fill else "none",
            "stroke": self.stroke.as_hex() if self.stroke else "none",
            "stroke-width": round(self.stroke_width * scale, 2),
            "stroke-opacity": self.opacity,
            "stroke-linecap": self.dash_capstyle,
        }

        if self.opacity != 1:
            attrs["fill-opacity"] = self.opacity

        if self.dash_array:
            attrs.update(_dash_array_attrs(self.dash_array, scale))
        return attrs

    def to_polygon_style(self):
        return PolygonStyle(
            fill=self.fill,
            stroke=self.stroke,
            stroke_width=self.stroke_width,
            opacity=self.opacity,
            zorder=self.zorder,
            dash_array=self.dash_array,
            dash_capstyle=self.dash_capstyle,
        )


class LineStyle(BaseStyle):
    """
    Styling properties for lines.
    """

    width: float = 2
    """Width of line in pixels"""

    stroke: Color | None = Color("#000")
    """Color of the line. Can be a hex, rgb, hsl, or word string."""

    dash_array: (
        Literal["solid", "dashed", "dashdot", "dotted"] | tuple[int, ...] | None
    ) = "solid"
    """Dash style of the line. Can be a predefined value in `DashArray` or a tuple [stroke dasharray](https://css-tricks.com/almanac/properties/s/stroke-dasharray/). A dash of `0` (e.g. `(0, 5)`) draws a row of evenly-spaced round dots instead of dashes -- pair it with `dash_capstyle=CapStyle.ROUND`, since a zero-length dash is only visible with a round cap."""

    cap_style: Literal["butt", "square", "round"] = "square"
    """Style of line/dash endpoints"""

    opacity: float = Field(default=1.0, ge=0, le=1)
    """Opacity (transparency) of the line (0 to 1)"""

    zorder: int = ZOrder.LAYER_2
    """Zorder of the line"""

    def css(self, scale: float = 1) -> dict:
        attrs = {
            "fill": "none",
            "stroke": self.stroke.as_hex() if self.stroke else "none",
            "stroke-width": round(self.width * scale, 2),
            "stroke-opacity": self.opacity,
            "stroke-linecap": self.cap_style,
        }
        attrs.update(_dash_array_attrs(self.dash_array, scale))

        return attrs


class PolygonStyle(BaseStyle):
    """
    Styling properties for polygons.
    """

    fill: Color | GradientStyle | None = Color("#c2c2c2")
    """
    Fill color of the polygon

    This can either be a single color (e.g. `#7abfff`) or a `GradientStyle` that defines a gradient. For example:

    ```
    GradientStyle(
        stops=(
            (0.0, "#7abfff"),
            (0.2, "#7abfff"),
            (0.9, "#568feb"),
            (1.0, "#3f7ee3"),  # the last stop should always be at 1.0
        ),
    )
    ```

    There are a few predefined gradients available as [style extensions](/reference-styling/#style-extensions).

    """

    stroke_width: float = 1
    """Width of the polygon's edge in pixels"""

    stroke: Color | None = Color("#000")
    """Edge color of the polygon"""

    dash_array: (
        Literal["solid", "dashed", "dashdot", "dotted"] | tuple[int, ...] | None
    ) = "solid"
    """Dash style of the polygon's stroke. Can be a predefined value in `DashArray` or a tuple [stroke dasharray](https://css-tricks.com/almanac/properties/s/stroke-dasharray/). A dash of `0` (e.g. `(0, 5)`) draws a row of evenly-spaced round dots instead of dashes -- pair it with `dash_capstyle=CapStyle.ROUND`, since a zero-length dash is only visible with a round cap."""

    dash_capstyle: Literal["butt", "square", "round"] = "round"
    """Style of dash endpoints. Matters even for a closed ring's dashes: a zero-length dash (as used for a dotted `dash_array`, e.g. `(0, 5)`) is only visible with a `round` cap -- `square`/`butt` caps render it as nothing."""

    opacity: float = Field(default=1.0, ge=0, le=1)
    """Opacity (transparency) of the polygon (0 to 1)"""

    zorder: int = ZOrder.LAYER_3
    """Zorder of the polygon"""

    def css(self, scale: float = 1.0) -> dict:
        solid_fill = self.fill is not None and not isinstance(self.fill, GradientStyle)
        attrs = {
            "fill": self.fill.as_hex() if solid_fill else "none",
            "stroke": self.stroke.as_hex() if self.stroke else "none",
            "stroke-width": round(self.stroke_width * scale, 2),
        }
        if self.opacity != 1:
            attrs["fill-opacity"] = self.opacity
            attrs["stroke-opacity"] = self.opacity

        if self.dash_array:
            attrs.update(_dash_array_attrs(self.dash_array, scale))
            attrs["stroke-linecap"] = self.dash_capstyle

        return attrs

    def to_marker_style(self, symbol: MarkerSymbol):
        return MarkerStyle(
            symbol=symbol,
            fill=self.fill,
            stroke=self.stroke.as_hex() if self.stroke else None,
            stroke_width=self.stroke_width,
            opacity=self.opacity,
            zorder=self.zorder,
            dash_array=self.dash_array,
            dash_capstyle=self.dash_capstyle,
        )


class ArrowStyle(PolygonStyle):
    body_width: float = 10
    """Width of the arrow's body, in pixels"""

    head_width: float = 30
    """Width of the arrow's head, in pixels"""

    head_height: float = 70
    """Height of the arrow's head, in pixels"""

    cap_style: Literal["butt", "square", "round"] = "butt"
    """Cap style of the arrow"""

    join_style: Literal["mitre", "bevel", "round"] = "mitre"
    """Join style of the arrow"""

    def shapely_kwargs(self):
        cap_styles = {
            "butt": "flat",
            "round": "round",
            "square": "square",
        }
        return {
            "cap_style": cap_styles[self.cap_style],
            "join_style": self.join_style,
        }


class LabelStyle(BaseStyle):
    """Styling properties for a label."""

    font_size: float = 24
    """Font size of the label, in pixels"""

    font_name: str | None = "Inter"
    """Name of the font to use"""

    font_family: str | None = "sans-serif"
    """Font family (e.g. 'monospace', 'sans-serif', 'serif', etc)"""

    font_weight: Literal[100, 200, 300, 400, 500, 600, 700, 800, 900] = 400
    """Font weight (e.g. normal, bold, ultra bold, etc)"""

    font_style: Literal["normal", "italic", "oblique"] = "normal"
    """Style of the label (e.g. normal, italic, etc)"""

    fill: Color = Color("#000")
    """Font's color"""

    opacity: float = Field(default=1.0, ge=0, le=1)
    """Opacity (transparency) of the label (0 to 1)"""

    anchor_point: Literal[
        "center",
        "left_center",
        "right_center",
        "top_left",
        "top_right",
        "top_center",
        "bottom_left",
        "bottom_right",
        "bottom_center",
    ] = "bottom_right"
    """Anchor point of label"""

    stroke_width: float = 0
    """Width of border (also known as 'halos') around the text, in pixels"""

    stroke: Color | None = None
    """Color of border (also known as 'halos') around the text"""

    offset_x: float | int | Literal["auto"] = 0
    """
    Horizontal offset of the label, in pixels. Negative values supported.
    
    **Auto Mode**: If the label is plotted as part of a marker (e.g. stars, via `marker()`, etc), then you can also
    specify the offset as `"auto"` which will calculate the offset automatically based on the marker's size and place
    the label just outside the marker (avoiding overlapping). To enable "auto" mode you have to specify BOTH offsets (x and y) as "auto."
    """

    offset_y: float | int | Literal["auto"] = 0
    """
    Vertical offset of the label, in pixels. Negative values supported.
    
    **Auto Mode**: If the label is plotted as part of a marker (e.g. stars, via `marker()`, etc), then you can also
    specify the offset as `"auto"` which will calculate the offset automatically based on the marker's size and place
    the label just outside the marker (avoiding overlapping). To enable "auto" mode you have to specify BOTH offsets (x and y) as "auto."
    """

    zorder: int = ZOrder.LAYER_4
    """Zorder of the label"""

    def css(self, scale: float = 1.0) -> dict:
        attrs = {
            "font-size": round(self.font_size * scale, 2),
            "font-family": f"{self.font_name}, {self.font_family}",
            "font-weight": self.font_weight,
            "font-style": self.font_style,
            "fill": self.fill.as_hex(),
            "fill-opacity": self.opacity,
        }
        if self.stroke_width and self.stroke:
            attrs["stroke"] = self.stroke.as_hex()
            attrs["stroke-width"] = round(self.stroke_width * scale, 2)
            attrs["stroke-opacity"] = self.opacity
            attrs["paint-order"] = "stroke fill"

        return attrs


class ObjectStyle(BaseStyle):
    """Defines the style for a sky object (e.g. star, DSO)"""

    marker: MarkerStyle = MarkerStyle()
    """Style for the object's marker (see [MarkerStyle][starplot.styles.MarkerStyle])"""

    label: LabelStyle = LabelStyle()
    """Style for the object's label (see [LabelStyle][starplot.styles.LabelStyle])"""


class PathStyle(BaseStyle):
    """Defines the style for a path (e.g. constellation lines)"""

    line: LineStyle = LineStyle()
    """Style for the line (see [LineStyle][starplot.styles.LineStyle])"""

    label: LabelStyle = LabelStyle()
    """Style for the path's label (see [LabelStyle][starplot.styles.LabelStyle])"""


class TableStyle(BaseStyle):
    """Defines the style for a table of data"""

    header: LabelStyle = LabelStyle(font_weight=FontWeight.BOLD)
    """Style for the table's header row text"""

    cell: LabelStyle = LabelStyle()
    """Style for the table's cell text"""

    border: LineStyle = LineStyle(stroke="#c5c5c5", width=1)
    """Style for the table's grid lines and outer border"""

    padding_top: int = 40
    """Padding above the table, in pixels. Creates space between the axes and the table."""

    alignment: Literal["left", "right", "center"] = "center"
    """Horizontal alignment of the table, relative to the axes region"""


class LegendStyle(BaseStyle):
    """Defines the style for the map legend."""

    location: Literal[
        "inside_top_left",
        "inside_top_right",
        "inside_bottom_right",
        "inside_bottom_left",
        "outside_top_left",
        "outside_top_right",
        "outside_bottom_right",
        "outside_bottom_left",
    ] = "inside_top_right"
    """Location of the legend, relative to the map area (inside or outside)"""

    background_color: Color = Color("#fff")
    """Background color of the legend box"""

    background_alpha: float = 1.0
    """Background's alpha (transparency)"""

    border_radius: float = 8.0
    """Border radius of legend box"""

    border_color: Color = Color("#c5c5c5")
    """Border color of the legend box"""

    border_width: float = 1
    """Border's width, in pixels"""

    zorder: int = ZOrder.LAYER_5
    """Zorder of the legend"""

    margin_x: float = 20
    """Horizontal margin (empty space) between legend and its anchor position."""

    margin_y: float = 20
    """Vertical margin (empty space) between legend and its anchor position."""

    padding_x: float = 40
    """Padding (in pixels) between the _outside_ of the legend and the map in the X axis. Negative numbers are supported."""

    padding_y: float = 20
    """Padding (in pixels) between the _outside_ of the legend and the map in the Y axis. Negative numbers are supported."""

    title: LabelStyle = LabelStyle(
        font_size=42,
        font_weight=FontWeight.BOLD,
    )
    """Style for the legend's labels (see [LabelStyle][starplot.styles.LabelStyle])"""

    label_padding: float = 24
    """Padding between legend labels"""

    labels: LabelStyle = LabelStyle(
        font_size=28,
        font_weight=FontWeight.NORMAL,
    )
    """Style for the legend's labels (see [LabelStyle][starplot.styles.LabelStyle])"""

    symbol_size: int = 28
    """Size of symbols in the legend, in pixels"""

    symbol_padding: float = 20
    """Padding between each symbol and its label"""


class TitleStyle(LabelStyle):
    padding_bottom: float = 20
    """Padding between bottom of title and the axes"""


class FigureStyle(BaseStyle):
    background: PolygonStyle = PolygonStyle(
        stroke_width=0,
        stroke="#000",
        fill="#fff",
    )
    """Background of the figure (the area surrounding the axes)"""

    padding: int = 0
    """Padding between the axes and edge of figure"""


class AxesStyle(BaseStyle):
    """Styling for the axes of the plot, which is where the map is plotted."""

    background: PolygonStyle = PolygonStyle(
        stroke_width=0,
        stroke="#000",
        fill="#fff",
    )
    """Background of the axes. This will always be plotted at the lowest Z-order."""

    border: LineStyle | None = LineStyle(width=2, stroke="#000")
    """
    Border drawn immediately outside the axes clip path (the entire stroke sits
    outside the clip path -- none of it overlaps the plot content). If `None`, 
    no border is drawn.

    If the plot also has gridline labels, then the gridline labels are plotted
    just outside the axes border, in the axes "frame" region.
    """


class PlotBaseStyle(BaseStyle):
    """
    Default base styles for all child styles that have these values set to `None` / null

    This is a way to apply some styles to everything in the plot, unless a style specifically sets one of these values.

    For example, if all object label styles have `font_name = None` then the `base` font name will be used.

    """

    font_name: str = "Inter"
    """Name of the base font to use if a style's font is set to `None`"""

    font_family: str = "sans-serif"
    """Font family (e.g. 'monospace', 'sans-serif', 'serif', etc) to use if a style's font family is set to `None`"""

    text_stroke_width: float = 0
    """Width of border (also known as 'halos' in map design) around text, in pixels"""

    text_stroke: Color | None = None
    """Color of border (also known as 'halos' in map design) around text if a style's value is set to `None`"""
