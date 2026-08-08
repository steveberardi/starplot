from typing import Optional, Union

from pydantic import BaseModel

from starplot.styles.base import BaseStyle
from starplot.styles.constants import (
    AnchorPointEnum,
    AlignmentEnum,
    FontStyleEnum,
    FontWeightEnum,
    GradientType,
    MarkerSymbolEnum,
    LineStyleEnum,
    CapStyleEnum,
    JoinStyleEnum,
    LegendLocationEnum,
    ZOrderEnum,
)
from starplot.styles.types import ColorStr, GradientStops


class MarkerStyle(BaseStyle):
    """
    Styling properties for markers.
    """

    color: Optional[ColorStr | GradientStops] = ColorStr("#000")
    """Fill color of marker. Can be a hex, rgb, hsl, or word string."""

    edge_color: Optional[ColorStr] = ColorStr("#000")
    """Edge color of marker. Can be a hex, rgb, hsl, or word string."""

    edge_width: float = 1
    """Edge width of marker, in pixels. Not available for all marker symbols."""

    line_style: Union[LineStyleEnum, tuple] = LineStyleEnum.SOLID
    """Edge line style. Can be a predefined value in `LineStyleEnum` or a [Matplotlib linestyle tuple](https://matplotlib.org/stable/gallery/lines_bars_and_markers/linestyles.html)."""

    dash_capstyle: CapStyleEnum = CapStyleEnum.PROJECTING
    """Style of dash endpoints"""

    dash_spacing: float | None = None
    """Spacing for dashes"""

    symbol: MarkerSymbolEnum = MarkerSymbolEnum.CIRCLE
    """Symbol for marker"""

    size: float = 22
    """Size of marker in pixels"""

    alpha: float = 1.0
    """Alpha value (controls transparency)"""

    gradient_type: GradientType = GradientType.RADIAL

    zorder: int = ZOrderEnum.LAYER_2
    """Zorder of marker"""

    def css(self, scale: float = 1) -> dict:
        solid_fill = self.color is not None and not isinstance(self.color, list)
        attrs = {
            "stroke": self.edge_color.as_hex() if self.edge_color else "none",
            "stroke-width": round(self.edge_width * scale, 2),
            "stroke-opacity": self.alpha,
            "stroke-linecap": CapStyleEnum(self.dash_capstyle).css(),
        }
        if solid_fill:
            attrs["fill"] = self.color.as_hex()

        if self.alpha != 1:
            attrs["fill-opacity"] = self.alpha

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
            fill_color=self.color,
            edge_color=self.edge_color,
            edge_width=self.edge_width,
            alpha=self.alpha,
            zorder=self.zorder,
            line_style=self.line_style,
        )


class LineStyle(BaseStyle):
    """
    Styling properties for lines.
    """

    width: float = 4
    """Width of line in pixels"""

    color: Optional[ColorStr] = ColorStr("#000")
    """Color of the line. Can be a hex, rgb, hsl, or word string."""

    style: Union[LineStyleEnum, tuple] = LineStyleEnum.SOLID
    """Style of the line (e.g. solid, dashed, etc). Can be a predefined value in `LineStyleEnum` or a [Matplotlib linestyle tuple](https://matplotlib.org/stable/gallery/lines_bars_and_markers/linestyles.html)."""

    cap_style: CapStyleEnum = CapStyleEnum.PROJECTING
    """Style of line/dash endpoints"""

    alpha: float = 1.0
    """Alpha value (controls transparency)"""

    zorder: int = ZOrderEnum.LAYER_2
    """Zorder of the line"""

    def css(self, scale: float = 1) -> dict:
        attrs = {
            "fill": "none",
            "stroke": self.color.as_hex() if self.color else "none",
            "stroke-width": round(self.width * scale, 2),
            "stroke-opacity": self.alpha,
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

    edge_width: float = 1
    """Width of the polygon's edge in pixels"""

    edge_color: Optional[ColorStr] = None
    """Edge color of the polygon"""

    fill_color: Optional[ColorStr | GradientStops] = None
    """Fill color of the polygon"""

    gradient_type: GradientType = GradientType.RADIAL

    line_style: Union[LineStyleEnum, tuple] = LineStyleEnum.SOLID
    """Edge line style. Can be a predefined value in `LineStyleEnum` or a tuple [stroke dasharray](https://css-tricks.com/almanac/properties/s/stroke-dasharray/)."""

    alpha: float = 1.0
    """Alpha value (controls transparency)"""

    zorder: int = ZOrderEnum.LAYER_3
    """Zorder of the polygon"""

    def css(self, scale: float = 1.0) -> dict:
        solid_fill = self.fill_color is not None and not isinstance(
            self.fill_color, list
        )
        attrs = {
            "fill": self.fill_color.as_hex() if solid_fill else "none",
            "stroke": self.edge_color.as_hex() if self.edge_color else "none",
            "stroke-width": round(self.edge_width * scale, 2),
        }
        if self.alpha != 1:
            attrs["fill-opacity"] = self.alpha
            attrs["stroke-opacity"] = self.alpha

        if isinstance(self.line_style, str):
            ls_css = LineStyleEnum(self.line_style).css()
            if ls_css:
                attrs["stroke-dasharray"] = ls_css
        elif self.line_style:
            attrs["stroke-dasharray"] = ",".join([str(n) for n in self.line_style])

        # attrs["stroke-linecap"] = CapStyleEnum(self.dash_capstyle).css()

        return attrs

    def to_marker_style(self, symbol: MarkerSymbolEnum):
        solid_fill = self.fill_color is not None and not isinstance(
            self.fill_color, list
        )
        fill_color = self.fill_color.as_hex() if solid_fill else None
        return MarkerStyle(
            symbol=symbol,
            color=fill_color,
            edge_color=self.edge_color.as_hex() if self.edge_color else None,
            edge_width=self.edge_width,
            alpha=self.alpha,
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

    font_weight: FontWeightEnum = FontWeightEnum.NORMAL
    """Font weight (e.g. normal, bold, ultra bold, etc)"""

    font_color: ColorStr = ColorStr("#000")
    """Font's color"""

    font_alpha: float = 1
    """Font's alpha (transparency)"""

    font_style: FontStyleEnum = FontStyleEnum.NORMAL
    """Style of the label (e.g. normal, italic, etc)"""

    font_name: Optional[str] = "Inter"
    """Name of the font to use"""

    font_family: Optional[str] = "sans-serif"
    """Font family (e.g. 'monospace', 'sans-serif', 'serif', etc)"""

    line_spacing: Optional[float] = None
    """Spacing between lines of text"""

    anchor_point: AnchorPointEnum = AnchorPointEnum.BOTTOM_RIGHT
    """Anchor point of label"""

    border_width: float = 0
    """Width of border (also known as 'halos') around the text, in pixels"""

    border_color: Optional[ColorStr] = None
    """Color of border (also known as 'halos') around the text"""

    offset_x: Union[float, int, str] = 0
    """
    Horizontal offset of the label, in pixels. Negative values supported.
    
    
    **Auto Mode** (_experimental_): If the label is plotted as part of a marker (e.g. stars, via `marker()`, etc), then you can also
    specify the offset as `"auto"` which will calculate the offset automatically based on the marker's size and place
    the label just outside the marker (avoiding overlapping). To enable "auto" mode you have to specify BOTH offsets (x and y) as "auto."
    """

    offset_y: Union[float, int, str] = 0
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
            "fill": self.font_color.as_hex(),
            "fill-opacity": self.font_alpha,
        }
        if self.border_width and self.border_color:
            attrs["stroke"] = self.border_color.as_hex()
            attrs["stroke-width"] = round(self.border_width * scale, 2)
            attrs["stroke-opacity"] = self.font_alpha
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
    """Defines the style for a table of data (see [Canvas.table][starplot.svg.canvas.Canvas.table])"""

    header: LabelStyle = LabelStyle(font_weight=FontWeightEnum.BOLD)
    """Style for the header row's text (see [LabelStyle][starplot.styles.LabelStyle])"""

    cell: LabelStyle = LabelStyle()
    """Style for the body cells' text (see [LabelStyle][starplot.styles.LabelStyle])"""

    border: LineStyle = LineStyle(color="#c5c5c5", width=1)
    """Style for the table's grid lines and outer border (see [LineStyle][starplot.styles.LineStyle])"""

    padding_top: int = 40
    """Padding above the table, in pixels. Creates space between the axes and the table."""

    alignment: AlignmentEnum = AlignmentEnum.CENTER
    """Horizontal alignment of the table, relative to the axes region"""


class LegendStyle(BaseStyle):
    """Defines the style for the map legend."""

    location: LegendLocationEnum = LegendLocationEnum.INSIDE_TOP_RIGHT
    """Location of the legend, relative to the map area (inside or outside)"""

    background_color: ColorStr = ColorStr("#fff")
    """Background color of the legend box"""

    background_alpha: float = 1.0
    """Background's alpha (transparency)"""

    border_radius: float = 8.0
    """Border radius of legend box"""

    border_color: ColorStr = ColorStr("#c5c5c5")
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
    background_color: ColorStr | None = ColorStr("#fff")

    padding: int = 0
    """Padding between the axes and edge of figure"""


class AxesStyle(BaseStyle):
    """Styling for the axes of the plot, which is where the map is plotted."""

    # TODO : since this may only have one sub element, maybe just change to:
    #    PlotStyle.axes: PolygonStyle

    background: PolygonStyle = PolygonStyle(
        edge_width=2, edge_color="#000", fill_color="#fff"
    )

    # background_color: GradientStops | ColorStr | None = ColorStr("#fff")
    """
    Background color of the axes.

    This can either be a single color (e.g. `#7abfff`) or a list that defines a gradient.

    For gradients, the list items should be tuples with two elements: a float that defines 
    the stop and a string that defines the color for that stop. For example:

    ```
    "background_color": [
        (0.0, "#7abfff"),
        (0.2, "#7abfff"),
        (0.9, "#568feb"),
        (1.0, "#3f7ee3"),  # the last stop should always be at 1.0
    ]
    ```

    There are a few predefined gradients available as [style extensions](/reference-styling/#style-extensions).
    """

    # background_gradient_direction: GradientType = GradientType.RADIAL
    """Direction of the background gradient (if applicable)"""

    # def has_gradient_background(self):
    #     return isinstance(self.background_color, list)
