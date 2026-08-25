from pydantic import Field

from starplot.styles.base import BaseStyle
from starplot.styles.constants import (
    AlignmentEnum,
    AnchorPointEnum,
    CapStyleEnum,
    FontStyleEnum,
    FontWeightEnum,
    GradientType,
    JoinStyleEnum,
    LegendLocationEnum,
    LineStyleEnum,
    MarkerSymbolEnum,
    ZOrderEnum,
)
from starplot.styles.types import Color, GradientStops


class MarkerStyle(BaseStyle):
    """
    Styling properties for markers.
    """

    fill: Color | GradientStops | None = Color("#000")
    """
    Fill color of the marker
    
    This can either be a single color (e.g. `#7abfff`) or a list that defines a gradient.

    For gradients, the list items should be tuples with two elements: a float that defines 
    the stop and a string that defines the color for that stop. For example:

    ```
    [
        (0.0, "#7abfff"),
        (0.2, "#7abfff"),
        (0.9, "#568feb"),
        (1.0, "#3f7ee3"),  # the last stop should always be at 1.0
    ]
    ```

    There are a few predefined gradients available as [style extensions](/reference-styling/#style-extensions).
    
    """

    stroke: Color | None = Color("#000")
    """Edge color of marker. Can be a hex, rgb, hsl, or word string."""

    stroke_width: float = 1
    """Edge width of marker, in pixels. Not available for all marker symbols."""

    line_style: LineStyleEnum | tuple = LineStyleEnum.SOLID
    """Edge line style. Can be a predefined value in `LineStyleEnum` or a [Matplotlib linestyle tuple](https://matplotlib.org/stable/gallery/lines_bars_and_markers/linestyles.html)."""

    dash_capstyle: CapStyleEnum = CapStyleEnum.PROJECTING
    """Style of dash endpoints"""

    dash_spacing: float | None = None
    """Spacing for dashes"""

    symbol: MarkerSymbolEnum = MarkerSymbolEnum.CIRCLE
    """Symbol for marker"""

    size: float = 24
    """Size of marker in pixels"""

    opacity: float = Field(default=1.0, ge=0, le=1)
    """Opacity (transparency) of the marker (0 to 1)"""

    gradient_type: GradientType = GradientType.RADIAL

    zorder: int = ZOrderEnum.LAYER_2
    """Zorder of marker"""

    def css(self, scale: float = 1) -> dict:
        solid_fill = self.fill is not None and not isinstance(self.fill, list)
        attrs = {
            "stroke": self.stroke.as_hex() if self.stroke else "none",
            "stroke-width": round(self.stroke_width * scale, 2),
            "stroke-opacity": self.opacity,
            "stroke-linecap": CapStyleEnum(self.dash_capstyle).css(),
        }
        if solid_fill:
            attrs["fill"] = self.fill.as_hex()

        if self.opacity != 1:
            attrs["fill-opacity"] = self.opacity

        if self.dash_spacing:
            attrs.update(
                {
                    "pathLength": 100,
                    "stroke-dasharray": f"0 {round(100 / self.dash_spacing, 4)}",
                }
            )
        return attrs

    def to_polygon_style(self):
        return PolygonStyle(
            fill=self.fill,
            stroke=self.stroke,
            stroke_width=self.stroke_width,
            opacity=self.opacity,
            zorder=self.zorder,
            line_style=self.line_style,
        )


class LineStyle(BaseStyle):
    """
    Styling properties for lines.
    """

    width: float = 2
    """Width of line in pixels"""

    stroke: Color | None = Color("#000")
    """Color of the line. Can be a hex, rgb, hsl, or word string."""

    style: LineStyleEnum | tuple = LineStyleEnum.SOLID
    """Style of the line (e.g. solid, dashed, etc). Can be a predefined value in `LineStyleEnum` or a [Matplotlib linestyle tuple](https://matplotlib.org/stable/gallery/lines_bars_and_markers/linestyles.html)."""

    cap_style: CapStyleEnum = CapStyleEnum.PROJECTING
    """Style of line/dash endpoints"""

    opacity: float = Field(default=1.0, ge=0, le=1)
    """Opacity (transparency) of the line (0 to 1)"""

    zorder: int = ZOrderEnum.LAYER_2
    """Zorder of the line"""

    def css(self, scale: float = 1) -> dict:
        attrs = {
            "fill": "none",
            "stroke": self.stroke.as_hex() if self.stroke else "none",
            "stroke-width": round(self.width * scale, 2),
            "stroke-opacity": self.opacity,
            "stroke-linecap": CapStyleEnum(self.cap_style).css(),
        }
        if isinstance(self.style, (str, LineStyleEnum)):
            ls_css = LineStyleEnum(self.style).css()
            if ls_css:
                attrs["stroke-dasharray"] = ls_css
        elif self.style:
            attrs["stroke-dasharray"] = ",".join([str(n) for n in self.style])

        return attrs


class PolygonStyle(BaseStyle):
    """
    Styling properties for polygons.
    """

    fill: Color | GradientStops | None = Color("#c2c2c2")
    """
    Fill color of the polygon
    
    This can either be a single color (e.g. `#7abfff`) or a list that defines a gradient.

    For gradients, the list items should be tuples with two elements: a float that defines 
    the stop and a string that defines the color for that stop. For example:

    ```
    [
        (0.0, "#7abfff"),
        (0.2, "#7abfff"),
        (0.9, "#568feb"),
        (1.0, "#3f7ee3"),  # the last stop should always be at 1.0
    ]
    ```

    There are a few predefined gradients available as [style extensions](/reference-styling/#style-extensions).
    
    """

    stroke_width: float = 1
    """Width of the polygon's edge in pixels"""

    stroke: Color | None = Color("#000")
    """Edge color of the polygon"""

    gradient_type: GradientType = GradientType.RADIAL

    line_style: LineStyleEnum | tuple = LineStyleEnum.SOLID
    """Edge line style. Can be a predefined value in `LineStyleEnum` or a tuple [stroke dasharray](https://css-tricks.com/almanac/properties/s/stroke-dasharray/)."""

    opacity: float = Field(default=1.0, ge=0, le=1)
    """Opacity (transparency) of the polygon (0 to 1)"""

    zorder: int = ZOrderEnum.LAYER_3
    """Zorder of the polygon"""

    def css(self, scale: float = 1.0) -> dict:
        solid_fill = self.fill is not None and not isinstance(self.fill, list)
        attrs = {
            "fill": self.fill.as_hex() if solid_fill else "none",
            "stroke": self.stroke.as_hex() if self.stroke else "none",
            "stroke-width": round(self.stroke_width * scale, 2),
        }
        if self.opacity != 1:
            attrs["fill-opacity"] = self.opacity
            attrs["stroke-opacity"] = self.opacity

        if isinstance(self.line_style, str):
            ls_css = LineStyleEnum(self.line_style).css()
            if ls_css:
                attrs["stroke-dasharray"] = ls_css
        elif self.line_style:
            attrs["stroke-dasharray"] = ",".join([str(n) for n in self.line_style])

        # attrs["stroke-linecap"] = CapStyleEnum(self.dash_capstyle).css()

        return attrs

    def to_marker_style(self, symbol: MarkerSymbolEnum):
        solid_fill = self.fill is not None and not isinstance(self.fill, list)
        fill_color = self.fill.as_hex() if solid_fill else None
        return MarkerStyle(
            symbol=symbol,
            fill=fill_color,
            stroke=self.stroke.as_hex() if self.stroke else None,
            stroke_width=self.stroke_width,
            opacity=self.opacity,
            zorder=self.zorder,
            line_style=self.line_style,
        )


class ArrowStyle(PolygonStyle):
    body_width: float = 10
    """Width of the arrow's body, in pixels"""

    head_width: float = 30
    """Width of the arrow's head, in pixels"""

    head_height: float = 70
    """Height of the arrow's head, in pixels"""

    cap_style: CapStyleEnum = CapStyleEnum.BUTT
    """Cap style of the arrow"""

    join_style: JoinStyleEnum = JoinStyleEnum.MITRE
    """Join style of the arrow"""

    def shapely_kwargs(self):
        cap_styles = {
            CapStyleEnum.BUTT: "flat",
            CapStyleEnum.ROUND: "round",
            CapStyleEnum.PROJECTING: "square",
        }
        return {
            "cap_style": cap_styles[self.cap_style],
            "join_style": self.join_style,
        }


class LabelStyle(BaseStyle):
    """
    Styling properties for a label.
    """

    font_size: float = 24
    """Font size of the label, in pixels"""

    font_name: str | None = "Inter"
    """Name of the font to use"""

    font_family: str | None = "sans-serif"
    """Font family (e.g. 'monospace', 'sans-serif', 'serif', etc)"""

    font_weight: FontWeightEnum = FontWeightEnum.NORMAL
    """Font weight (e.g. normal, bold, ultra bold, etc)"""

    font_style: FontStyleEnum = FontStyleEnum.NORMAL
    """Style of the label (e.g. normal, italic, etc)"""

    fill: Color = Color("#000")
    """Font's color"""

    opacity: float = Field(default=1.0, ge=0, le=1)
    """Opacity (transparency) of the label (0 to 1)"""

    line_spacing: float | None = None
    """Spacing between lines of text"""

    anchor_point: AnchorPointEnum = AnchorPointEnum.BOTTOM_RIGHT
    """Anchor point of label"""

    stroke_width: float = 0
    """Width of border (also known as 'halos') around the text, in pixels"""

    stroke: Color | None = None
    """Color of border (also known as 'halos') around the text"""

    offset_x: float | int | str = 0
    """
    Horizontal offset of the label, in pixels. Negative values supported.
    
    
    **Auto Mode** (_experimental_): If the label is plotted as part of a marker (e.g. stars, via `marker()`, etc), then you can also
    specify the offset as `"auto"` which will calculate the offset automatically based on the marker's size and place
    the label just outside the marker (avoiding overlapping). To enable "auto" mode you have to specify BOTH offsets (x and y) as "auto."
    """

    offset_y: float | int | str = 0
    """
    Vertical offset of the label, in pixels. Negative values supported.
    
    **Auto Mode** (_experimental_): If the label is plotted as part of a marker (e.g. stars, via `marker()`, etc), then you can also
    specify the offset as `"auto"` which will calculate the offset automatically based on the marker's size and place
    the label just outside the marker (avoiding overlapping). To enable "auto" mode you have to specify BOTH offsets (x and y) as "auto."
    """

    zorder: int = ZOrderEnum.LAYER_4
    """Zorder of the label"""

    def css(self, scale: float = 1.0) -> dict:
        attrs = {
            "font-size": round(self.font_size * scale, 2),
            "font-family": f"{self.font_name}, {self.font_family}",
            "font-weight": FontWeightEnum(self.font_weight).value,
            "font-style": FontStyleEnum(self.font_style).value,
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

    header: LabelStyle = LabelStyle(font_weight=FontWeightEnum.BOLD)
    """Style for the table's header row text"""

    cell: LabelStyle = LabelStyle()
    """Style for the table's cell text"""

    border: LineStyle = LineStyle(stroke="#c5c5c5", width=1)
    """Style for the table's grid lines and outer border"""

    padding_top: int = 40
    """Padding above the table, in pixels. Creates space between the axes and the table."""

    alignment: AlignmentEnum = AlignmentEnum.CENTER
    """Horizontal alignment of the table, relative to the axes region"""


class LegendStyle(BaseStyle):
    """Defines the style for the map legend."""

    location: LegendLocationEnum = LegendLocationEnum.INSIDE_TOP_RIGHT
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

    zorder: int = ZOrderEnum.LAYER_5
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
        font_weight=FontWeightEnum.BOLD,
    )
    """Style for the legend's labels (see [LabelStyle][starplot.styles.LabelStyle])"""

    label_padding: float = 24
    """Padding between legend labels"""

    labels: LabelStyle = LabelStyle(
        font_size=28,
        font_weight=FontWeightEnum.NORMAL,
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
