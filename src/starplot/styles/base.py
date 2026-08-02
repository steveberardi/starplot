import json

from enum import Enum
from pathlib import Path
from typing import Optional, Union

import yaml
from pydantic import BaseModel, AfterValidator
from pydantic_extra_types.color import Color
from pydantic.functional_serializers import PlainSerializer
from typing_extensions import Annotated

from starplot.models.dso import DsoType
from starplot.styles.helpers import merge_dict

ColorStr = Annotated[
    Color,
    PlainSerializer(
        lambda c: c.as_hex() if c and c != "none" else None,
        return_type=str,
    ),
]


def _validate_stops(stops: list[tuple[float, str]]) -> list[tuple[float, str]]:
    if not stops:
        raise ValueError("gradient must have at least one stop")
    if stops[-1][0] != 1.0:
        raise ValueError("the last stop should always be at 1.0")
    return stops


GradientStops = Annotated[
    list[tuple[float, ColorStr]],
    AfterValidator(_validate_stops),
    PlainSerializer(
        lambda stops: [(offset, c.as_hex() if c else None) for offset, c in stops],
        return_type=list,
    ),
]

HERE = Path(__file__).resolve().parent

PI = 3.141592653589793
SQR_2 = 1.41421356237


class BaseStyle(BaseModel):
    __hash__ = object.__hash__

    class Config:
        extra = "forbid"
        use_enum_values = True
        validate_assignment = True

    def __enter__(self):
        self._original = self.model_copy(deep=True)
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        for field_name in self.__pydantic_fields__.keys():
            original_value = getattr(self._original, field_name)
            setattr(self, field_name, original_value)

    @property
    def css_string(self) -> str:
        return " ".join([f'{k}="{v}"' for k, v in self.css().items()])


class GradientType(str, Enum):
    LINEAR = "linear"
    RADIAL = "radial"


class FontWeightEnum(int, Enum):
    """Options for font weight."""

    THIN = 100
    EXTRA_LIGHT = 200
    LIGHT = 300
    NORMAL = 400
    MEDIUM = 500
    SEMI_BOLD = 600
    BOLD = 700
    EXTRA_BOLD = 800
    HEAVY = 900


class FontStyleEnum(str, Enum):
    NORMAL = "normal"
    ITALIC = "italic"
    OBLIQUE = "oblique"


class MarkerSymbolEnum(str, Enum):
    """Options for marker symbols"""

    PLUS = "plus"
    """+"""

    CIRCLE = "circle"
    """\u25cf"""

    SQUARE = "square"
    """\u25a0"""

    STAR = "star"
    """\u2605"""

    SUN = "sun"
    """\u263c"""

    DIAMOND = "diamond"
    """\u25c6"""

    TRIANGLE = "triangle"
    """\u23f6"""

    CIRCLE_CROSS = "circle_cross"
    """\u1aa0"""

    CIRCLE_CROSSHAIR = "circle_crosshair"
    """No preview available, but this is the standard symbol for planetary nebulae"""

    CIRCLE_LINE = "circle_line"
    """\u29b5  the standard symbol for double stars"""

    COMET = "comet"
    """\u2604"""

    STAR_4 = "star_4"
    """\u2726"""

    STAR_8 = "star_8"
    """\u2734"""

    ELLIPSE = "ellipse"
    """\u2b2d"""


class LineStyleEnum(str, Enum):
    SOLID = "solid"
    DASHED = "dashed"
    DASHED_DOTS = "dashdot"
    DOTTED = "dotted"

    def css(self) -> str | None:
        return {
            LineStyleEnum.SOLID: None,
            LineStyleEnum.DASHED: "6,3",
            LineStyleEnum.DOTTED: "2,3",
            LineStyleEnum.DASHED_DOTS: "6,3,1,3",
        }.get(self.value)


class CapStyleEnum(str, Enum):
    BUTT = "butt"
    PROJECTING = "projecting"
    ROUND = "round"

    def css(self) -> str | None:
        return {
            CapStyleEnum.BUTT: "butt",
            CapStyleEnum.ROUND: "round",
            CapStyleEnum.PROJECTING: "square",
        }.get(self.value)


class JoinStyleEnum(str, Enum):
    MITRE = "mitre"
    BEVEL = "bevel"
    ROUND = "round"


class LegendLocationEnum(str, Enum):
    """Options for the location of the map legend, relative to the axes"""

    INSIDE_TOP_LEFT = "inside top left"
    INSIDE_TOP_RIGHT = "inside top right"
    INSIDE_BOTTOM_RIGHT = "inside bottom right"
    INSIDE_BOTTOM_LEFT = "inside bottom left"

    OUTSIDE_TOP_LEFT = "outside top left"
    OUTSIDE_TOP_RIGHT = "outside top right"
    OUTSIDE_BOTTOM_RIGHT = "outside bottom right"
    OUTSIDE_BOTTOM_LEFT = "outside bottom left"


class AnchorPointEnum(str, Enum):
    """Options for the anchor point of labels"""

    CENTER = "center"
    LEFT_CENTER = "left center"
    RIGHT_CENTER = "right center"
    TOP_LEFT = "top left"
    TOP_RIGHT = "top right"
    TOP_CENTER = "top center"
    BOTTOM_LEFT = "bottom left"
    BOTTOM_RIGHT = "bottom right"
    BOTTOM_CENTER = "bottom center"

    @staticmethod
    def from_str(value: str) -> "AnchorPointEnum":
        options = {ap.value: ap for ap in AnchorPointEnum}
        return options.get(value)


class AlignmentEnum(str, Enum):
    """Alignment options for the legend's title and entries"""

    LEFT = "left"
    RIGHT = "right"
    CENTER = "center"


class ZOrderEnum(int, Enum):
    """
    Z Order presets for managing layers
    """

    LAYER_1 = -2_000
    """Bottom layer"""

    LAYER_2 = -1_000

    LAYER_3 = 0
    """Middle layer"""

    LAYER_4 = 1_000

    LAYER_5 = 2_000
    """Top layer"""


class MarkerStyle(BaseStyle):
    """
    Styling properties for markers.
    """

    color: Optional[ColorStr | GradientStops] = ColorStr("#000")
    """Fill color of marker. Can be a hex, rgb, hsl, or word string."""

    edge_color: Optional[ColorStr] = ColorStr("#000")
    """Edge color of marker. Can be a hex, rgb, hsl, or word string."""

    edge_width: float = 1
    """Edge width of marker, in points. Not available for all marker symbols."""

    line_style: Union[LineStyleEnum, tuple] = LineStyleEnum.SOLID
    """Edge line style. Can be a predefined value in `LineStyleEnum` or a [Matplotlib linestyle tuple](https://matplotlib.org/stable/gallery/lines_bars_and_markers/linestyles.html)."""

    dash_capstyle: CapStyleEnum = CapStyleEnum.PROJECTING
    """Style of dash endpoints"""

    dash_spacing: float | None = None
    """SVG ONLY - Spacing for dashes"""

    symbol: MarkerSymbolEnum = MarkerSymbolEnum.CIRCLE
    """Symbol for marker"""

    size: float = 22
    """Size of marker in points"""

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
    """Width of line in points"""

    color: Optional[ColorStr] = ColorStr("#000")
    """Color of the line. Can be a hex, rgb, hsl, or word string."""

    style: Union[LineStyleEnum, tuple] = LineStyleEnum.SOLID
    """Style of the line (e.g. solid, dashed, etc). Can be a predefined value in `LineStyleEnum` or a [Matplotlib linestyle tuple](https://matplotlib.org/stable/gallery/lines_bars_and_markers/linestyles.html)."""

    dash_capstyle: CapStyleEnum = CapStyleEnum.PROJECTING
    """Style of dash endpoints"""

    alpha: float = 1.0
    """Alpha value (controls transparency)"""

    zorder: int = ZOrderEnum.LAYER_2
    """Zorder of the line"""

    edge_width: int = 0
    """Width of the line's edge in points. _If the width or color is falsey then the line will NOT be drawn with an edge._"""

    edge_color: Optional[ColorStr] = None
    """Edge color of the line. _If the width or color is falsey then the line will NOT be drawn with an edge._"""

    def css(self, scale: float = 1) -> dict:
        attrs = {
            "fill": "none",
            "stroke": self.color.as_hex() if self.color else "none",
            "stroke-width": round(self.width * scale, 2),
            "stroke-opacity": self.alpha,
            "stroke-linecap": CapStyleEnum(self.dash_capstyle).css(),
        }
        if isinstance(self.style, (str, LineStyleEnum)):
            ls_css = LineStyleEnum(self.style).css()
            if ls_css:
                attrs["stroke-dasharray"] = ls_css
        elif self.style:
            attrs["stroke-dasharray"] = ",".join([str(n) for n in self.style[1]])

        return attrs


class PolygonStyle(BaseStyle):
    """
    Styling properties for polygons.
    """

    edge_width: float = 1
    """Width of the polygon's edge in points"""

    edge_color: Optional[ColorStr] = None
    """Edge color of the polygon"""

    fill_color: Optional[ColorStr | GradientStops] = None
    """Fill color of the polygon"""

    gradient_type: GradientType = GradientType.RADIAL

    line_style: Union[LineStyleEnum, tuple] = LineStyleEnum.SOLID
    """Edge line style. Can be a predefined value in `LineStyleEnum` or a tuple [stroke dasharray](https://css-tricks.com/almanac/properties/s/stroke-dasharray/)."""

    alpha: float = 1.0
    """Alpha value (controls transparency)"""

    zorder: int = 100
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
            attrs["stroke-dasharray"] = ",".join([str(n) for n in self.line_style[1]])

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

    font_size: float = 15
    """Font size of the label, in points"""

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
    """Width of border (also known as 'halos') around the text, in points"""

    border_color: Optional[ColorStr] = None
    """Color of border (also known as 'halos') around the text"""

    offset_x: Union[float, int, str] = 0
    """
    Horizontal offset of the label, in points. Negative values supported.
    
    
    **Auto Mode** (_experimental_): If the label is plotted as part of a marker (e.g. stars, via `marker()`, etc), then you can also
    specify the offset as `"auto"` which will calculate the offset automatically based on the marker's size and place
    the label just outside the marker (avoiding overlapping). To enable "auto" mode you have to specify BOTH offsets (x and y) as "auto."
    """

    offset_y: Union[float, int, str] = 0
    """
    Vertical offset of the label, in points. Negative values supported.
    
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

    padding_top: int = 20
    """Padding above the table, in pixels. Creates space between the axes and the table."""


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
    #    PlotStyle.axes_background: PolygonStyle

    background: PolygonStyle = PolygonStyle(
        edge_width=2, edge_color="#000", fill_color="#fff"
    )

    background_color: GradientStops | ColorStr | None = ColorStr("#fff")
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

    background_gradient_direction: GradientType = GradientType.RADIAL
    """Direction of the background gradient (if applicable)"""

    def has_gradient_background(self):
        return isinstance(self.background_color, list)


class PlotStyle(BaseStyle):
    """
    Defines the styling for a plot
    """

    axes: AxesStyle = AxesStyle()
    """Styling for the axes of the plot, which is where the map is plotted."""

    axes_background: PolygonStyle = PolygonStyle(
        edge_width=2, edge_color="#000", fill_color="#fff"
    )

    figure: FigureStyle = FigureStyle()
    """
    Styling for the figure of the plot, which is the surrounding region outside the axes. 
    
    This area can include:
    
    - Title of the plot
    - Legend (if plotted 'outside')
    - Padding between the axes (map region) and edge of image
    
    """

    text_border_width: int = 2
    """Text border (aka halos) width. This will apply to _all_ text labels on the plot. If you'd like to control these borders by object type, then set this global width to `0` and refer to the label style's `border_width` and `border_color` properties."""

    text_border_color: ColorStr = ColorStr("#fff")

    # Borders
    border_font_size: int = 18
    border_font_weight: FontWeightEnum = FontWeightEnum.BOLD
    border_font_color: ColorStr = ColorStr("#000")
    border_line_color: ColorStr = ColorStr("#000")
    border_bg_color: ColorStr = ColorStr("#fff")

    # Title
    title: TitleStyle = TitleStyle(
        font_size=70,
        font_weight=FontWeightEnum.BOLD,
        zorder=ZOrderEnum.LAYER_5,
        line_spacing=150,
        anchor_point=AnchorPointEnum.BOTTOM_CENTER,
        padding_bottom=24,
    )
    """Styling for the title of the plot"""

    table: TableStyle = TableStyle(
        header=LabelStyle(
            font_size=32,
            zorder=ZOrderEnum.LAYER_5,
            font_family="Inter",
            font_weight=FontWeightEnum.BOLD,
            anchor_point=AnchorPointEnum.BOTTOM_CENTER,
        ),
        cell=LabelStyle(
            font_size=32,
            zorder=ZOrderEnum.LAYER_5,
            font_family="Inter",
            anchor_point=AnchorPointEnum.BOTTOM_CENTER,
        ),
        padding_top=24,
    )
    """Styling for the data table of the plot, which is always plotted below the axes."""

    # Stars
    star: ObjectStyle = ObjectStyle(
        marker=MarkerStyle(
            zorder=ZOrderEnum.LAYER_3 + 1,
            size=40,
            edge_color=None,
        ),
        label=LabelStyle(
            font_size=24,
            font_weight=FontWeightEnum.BOLD,
            zorder=ZOrderEnum.LAYER_3 + 2,
            offset_x="auto",
            offset_y="auto",
        ),
    )
    """Styling for stars *(see [`ObjectStyle`][starplot.styles.ObjectStyle])*"""

    bayer_labels: LabelStyle = LabelStyle(
        font_size=21,
        font_weight=FontWeightEnum.EXTRA_LIGHT,
        font_name="GFS Didot",
        zorder=ZOrderEnum.LAYER_4,
        anchor_point=AnchorPointEnum.TOP_LEFT,
        offset_x="auto",
        offset_y="auto",
    )
    """Styling for Bayer labels of stars"""

    flamsteed_labels: LabelStyle = LabelStyle(
        font_size=13,
        font_weight=FontWeightEnum.NORMAL,
        zorder=ZOrderEnum.LAYER_4,
        anchor_point=AnchorPointEnum.BOTTOM_LEFT,
        offset_x="auto",
        offset_y="auto",
    )
    """Styling for Flamsteed number labels of stars"""

    planets: ObjectStyle = ObjectStyle(
        marker=MarkerStyle(
            symbol=MarkerSymbolEnum.CIRCLE,
            size=28,
            zorder=ZOrderEnum.LAYER_3,
            alpha=1,
        ),
        label=LabelStyle(
            font_size=28,
            font_weight=FontWeightEnum.BOLD,
            offset_x="auto",
            offset_y="auto",
        ),
    )
    """Styling for planets"""

    moon: ObjectStyle = ObjectStyle(
        marker=MarkerStyle(
            symbol=MarkerSymbolEnum.CIRCLE,
            size=50,
            color="#c8c8c8",
            alpha=1,
            zorder=ZOrderEnum.LAYER_4,
        ),
        label=LabelStyle(
            font_size=28,
            font_weight=FontWeightEnum.BOLD,
            offset_x="auto",
            offset_y="auto",
        ),
    )
    """Styling for the moon"""

    sun: ObjectStyle = ObjectStyle(
        marker=MarkerStyle(
            symbol=MarkerSymbolEnum.SUN,
            size=80,
            color="#000",
            zorder=ZOrderEnum.LAYER_4 - 100,
        ),
        label=LabelStyle(
            font_size=28,
            font_weight=FontWeightEnum.BOLD,
        ),
    )
    """Styling for the Sun"""

    # Deep Sky Objects (DSOs)
    dso_open_cluster: ObjectStyle = ObjectStyle(
        marker=MarkerStyle(
            symbol=MarkerSymbolEnum.CIRCLE,
            line_style=(0, (1, 2)),
            dash_spacing=28,
            dash_capstyle=CapStyleEnum.ROUND,
            edge_width=2,
            zorder=ZOrderEnum.LAYER_3 - 1,
        ),
        label=LabelStyle(offset_x="auto", offset_y="auto"),
    )
    """Styling for open star clusters"""

    dso_association_stars: ObjectStyle = ObjectStyle(
        marker=MarkerStyle(
            symbol=MarkerSymbolEnum.CIRCLE,
            line_style=(0, (1, 2)),
            dash_spacing=28,
            dash_capstyle=CapStyleEnum.ROUND,
            edge_width=2,
            zorder=ZOrderEnum.LAYER_3 - 1,
        ),
        label=LabelStyle(offset_x="auto", offset_y="auto"),
    )
    """Styling for associations of stars"""

    dso_globular_cluster: ObjectStyle = ObjectStyle(
        marker=MarkerStyle(
            symbol=MarkerSymbolEnum.CIRCLE_CROSS,
            color="#555",
            alpha=0.8,
            edge_width=1.2,
            zorder=ZOrderEnum.LAYER_3 - 1,
        ),
        label=LabelStyle(offset_x="auto", offset_y="auto"),
    )
    """Styling for globular star clusters"""

    dso_galaxy: ObjectStyle = ObjectStyle(
        marker=MarkerStyle(
            symbol=MarkerSymbolEnum.ELLIPSE,
            zorder=ZOrderEnum.LAYER_3 - 1,
        ),
        label=LabelStyle(offset_x="auto", offset_y="auto"),
    )
    """Styling for galaxies"""

    dso_nebula: ObjectStyle = ObjectStyle(
        marker=MarkerStyle(
            symbol=MarkerSymbolEnum.SQUARE,
            zorder=ZOrderEnum.LAYER_3 - 1,
        ),
        label=LabelStyle(offset_x="auto", offset_y="auto"),
    )
    """Styling for nebulas"""

    dso_planetary_nebula: ObjectStyle = ObjectStyle(
        marker=MarkerStyle(
            symbol=MarkerSymbolEnum.CIRCLE_CROSSHAIR,
            edge_width=1.6,
            size=26,
            zorder=ZOrderEnum.LAYER_3 - 1,
        ),
        label=LabelStyle(offset_x="auto", offset_y="auto"),
    )
    """Styling for planetary nebulas"""

    dso_double_star: ObjectStyle = ObjectStyle(
        marker=MarkerStyle(
            symbol=MarkerSymbolEnum.CIRCLE_LINE,
            zorder=ZOrderEnum.LAYER_3 - 1,
        ),
        label=LabelStyle(offset_x=1, offset_y=-1),
    )
    """Styling for double stars"""

    dso_dark_nebula: ObjectStyle = ObjectStyle(
        marker=MarkerStyle(
            symbol=MarkerSymbolEnum.SQUARE,
            color="#000",
            zorder=ZOrderEnum.LAYER_3 - 1,
        ),
        label=LabelStyle(),
    )
    """Styling for dark nebulas"""

    dso_supernova_remnant: ObjectStyle = ObjectStyle(
        marker=MarkerStyle(
            symbol=MarkerSymbolEnum.SQUARE,
            color="#000",
            zorder=ZOrderEnum.LAYER_3 - 1,
        ),
        label=LabelStyle(),
    )
    """Styling for supernova remnants"""

    dso_nova_star: ObjectStyle = ObjectStyle(
        marker=MarkerStyle(
            symbol=MarkerSymbolEnum.SQUARE,
            color="#000",
            zorder=ZOrderEnum.LAYER_3 - 1,
        ),
        label=LabelStyle(),
    )
    """Styling for nova stars"""

    dso_nonexistant: ObjectStyle = ObjectStyle(
        marker=MarkerStyle(
            symbol=MarkerSymbolEnum.SQUARE,
            color="#000",
            zorder=ZOrderEnum.LAYER_3 - 1,
        ),
        label=LabelStyle(),
    )
    """Styling for 'nonexistent' (as designated by OpenNGC) deep sky objects"""

    dso_unknown: ObjectStyle = ObjectStyle(
        marker=MarkerStyle(
            symbol=MarkerSymbolEnum.SQUARE,
            color="#000",
            zorder=ZOrderEnum.LAYER_3 - 1,
        ),
        label=LabelStyle(),
    )
    """Styling for 'unknown' (as designated by OpenNGC) types of deep sky objects"""

    dso_duplicate: ObjectStyle = ObjectStyle(
        marker=MarkerStyle(
            symbol=MarkerSymbolEnum.SQUARE,
            color="#000",
            zorder=ZOrderEnum.LAYER_3 - 1,
        ),
        label=LabelStyle(),
    )
    """Styling for 'duplicate record' (as designated by OpenNGC) types of deep sky objects"""

    constellation_lines: LineStyle = LineStyle(
        color="#c8c8c8", zorder=ZOrderEnum.LAYER_3
    )
    """Styling for constellation lines"""

    constellation_borders: LineStyle = LineStyle(
        color="#000",
        width=1.8,
        # style=LineStyleEnum.DASHED,
        style=(0, (5, 5)),
        alpha=0.5,
        zorder=ZOrderEnum.LAYER_3,
    )
    """Styling for constellation borders"""

    constellation_labels: LabelStyle = LabelStyle(
        font_size=21,
        font_weight=FontWeightEnum.NORMAL,
        zorder=ZOrderEnum.LAYER_3,
        anchor_point=AnchorPointEnum.CENTER,
    )
    """Styling for constellation labels"""

    # Milky Way
    milky_way: PolygonStyle = PolygonStyle(
        fill_color="#d9d9d9",
        alpha=0.36,
        edge_width=0,
        zorder=ZOrderEnum.LAYER_1,
    )
    """Styling for the Milky Way (only applies to map plots)"""

    # Legend
    legend: LegendStyle = LegendStyle()
    """Styling for legend"""

    # Gridlines
    gridlines: PathStyle = PathStyle(
        line=LineStyle(
            color="#888",
            width=1,
            style=LineStyleEnum.SOLID,
            alpha=0.6,
            zorder=ZOrderEnum.LAYER_2,
        ),
        label=LabelStyle(
            font_size=28,
            font_color="#000",
            font_alpha=1,
            font_weight=FontWeightEnum.NORMAL,
            anchor_point=AnchorPointEnum.BOTTOM_CENTER,
            zorder=ZOrderEnum.LAYER_5 + 1000,
        ),
    )
    """Styling for gridlines (including Right Ascension / Declination labels). *Only applies to map plots*."""

    ecliptic: PathStyle = PathStyle(
        line=LineStyle(
            color="#777",
            width=3,
            style=(0, (2, 6)),
            dash_capstyle=CapStyleEnum.ROUND,
            alpha=1,
            zorder=ZOrderEnum.LAYER_3 - 1,
        ),
        label=LabelStyle(
            font_size=21,
            font_color="#777",
            font_alpha=1,
            font_weight=FontWeightEnum.NORMAL,
            border_width=8,
            border_color="#000",
            zorder=ZOrderEnum.LAYER_3,
        ),
    )
    """Styling for the Ecliptic"""

    celestial_equator: PathStyle = PathStyle(
        line=LineStyle(
            color="#999",
            width=3,
            style=LineStyleEnum.DASHED_DOTS,
            alpha=1,
            zorder=ZOrderEnum.LAYER_3,
        ),
        label=LabelStyle(
            font_size=21,
            font_color="#999",
            font_weight=FontWeightEnum.NORMAL,
            font_alpha=1,
            border_width=8,
            border_color="#000",
            zorder=ZOrderEnum.LAYER_3,
        ),
    )
    """Styling for the Celestial Equator"""

    galactic_equator: PathStyle = PathStyle(
        line=LineStyle(
            color="#999",
            width=3,
            style=LineStyleEnum.SOLID,
            alpha=0.65,
            zorder=ZOrderEnum.LAYER_3,
        ),
        label=LabelStyle(
            font_size=21,
            font_color="#7c7c7c",
            font_weight=FontWeightEnum.NORMAL,
            font_alpha=1,
            border_width=8,
            border_color="#000",
            zorder=ZOrderEnum.LAYER_3,
        ),
    )
    """Styling for the Galactic Equator"""

    horizon: PathStyle = PathStyle(
        line=LineStyle(
            color="#fff",
            width=110,
            edge_width=4,
            edge_color="#000",
            style=LineStyleEnum.SOLID,
            dash_capstyle=CapStyleEnum.ROUND,
            alpha=1,
            zorder=ZOrderEnum.LAYER_5,
        ),
        label=LabelStyle(
            anchor_point=AnchorPointEnum.CENTER,
            font_color="#000",
            font_size=70,
            font_weight=FontWeightEnum.BOLD,
            zorder=ZOrderEnum.LAYER_5,
        ),
    )
    """Styling for the horizon"""

    zenith: ObjectStyle = ObjectStyle(
        marker=MarkerStyle(
            symbol=MarkerSymbolEnum.TRIANGLE,
            size=24,
            color="#000",
            alpha=0.8,
        ),
        label=LabelStyle(font_size=14, font_weight=FontWeightEnum.BOLD),
    )
    """Styling for the zenith marker"""

    optic_fov: PolygonStyle = PolygonStyle(
        fill_color=None,
        edge_color="red",
        line_style=[1, [2, 3]],
        edge_width=3,
        zorder=-1000,
    )
    """Styling for optic fields of view"""

    arrow: ArrowStyle = ArrowStyle(
        fill_color="hsl(0, 99%, 31%)",
        edge_color="#ff0019",
        edge_width=2,
        zorder=ZOrderEnum.LAYER_4,
    )
    """Styling for optic fields of view"""

    def get_dso_style(self, dso_type: DsoType):
        """Returns the style for a DSO type"""
        styles_by_type = {
            # Star Clusters ----------
            DsoType.OPEN_CLUSTER: self.dso_open_cluster,
            DsoType.GLOBULAR_CLUSTER: self.dso_globular_cluster,
            # Galaxies ----------
            DsoType.GALAXY: self.dso_galaxy,
            DsoType.GALAXY_PAIR: self.dso_galaxy,
            DsoType.GALAXY_TRIPLET: self.dso_galaxy,
            DsoType.GROUP_OF_GALAXIES: self.dso_galaxy,
            # Nebulas ----------
            DsoType.NEBULA: self.dso_nebula,
            DsoType.PLANETARY_NEBULA: self.dso_planetary_nebula,
            DsoType.EMISSION_NEBULA: self.dso_nebula,
            DsoType.STAR_CLUSTER_NEBULA: self.dso_nebula,
            DsoType.REFLECTION_NEBULA: self.dso_nebula,
            DsoType.HII_IONIZED_REGION: self.dso_nebula,
            # Stars ----------
            DsoType.STAR: self.star,
            DsoType.DOUBLE_STAR: self.dso_double_star,
            DsoType.ASSOCIATION_OF_STARS: self.dso_association_stars,
            # Others ----------
            DsoType.DARK_NEBULA: self.dso_dark_nebula,
            DsoType.SUPERNOVA_REMNANT: self.dso_supernova_remnant,
            DsoType.NOVA_STAR: self.dso_nova_star,
            DsoType.NONEXISTENT: self.dso_nonexistant,
            DsoType.UNKNOWN: self.dso_unknown,
            DsoType.DUPLICATE_RECORD: self.dso_duplicate,
        }
        return styles_by_type.get(dso_type)

    @staticmethod
    def load_from_file(filename: str) -> "PlotStyle":
        """
        Load a style from a YAML file. The returned style is an extension of the default PlotStyle
        (see [`PlotStyle.extend`][starplot.styles.PlotStyle.extend]), so you only need to define
        properties you want to override from the default.

        Args:
            filename: Filename of style file

        Returns:
            PlotStyle: A new instance of a PlotStyle
        """
        with open(filename, "r") as sfile:
            style = yaml.safe_load(sfile)
            return PlotStyle().extend(style)

    def dump_to_file(self, filename: str) -> None:
        """
        Save the style to a YAML file. ALL style properties will be written to the file.

        Args:
            filename: Filename of style file
        """
        with open(filename, "w") as outfile:
            style_json = self.model_dump_json()
            style_yaml = yaml.dump(json.loads(style_json))
            outfile.write(style_yaml)

    def extend(self, *args, **kwargs) -> "PlotStyle":
        """
        Adds one or more dicts of style overrides to the style and returns a new instance with
        those overrides.

        Styles are added in sequential order, so if the first style arg has a property
        that is also in the last style arg, then the resulting style will have the value
        from the last style (similar to how CSS works).

        ???- tip "Example Usage"
            Create an extension of the default style with the light blue color scheme, map optimizations,
            and change the constellation line color to red:

            ```python

            new_style = PlotStyle().extend(
                styles.extensions.BLUE_LIGHT,
                styles.extensions.MAP,
                {
                    "constellation": {"line": {"color": "#e12d2d"}},
                },
            )
            ```

        Args:
            args: One or more dicts of styles to add

        Returns:
            PlotStyle: A new instance of a PlotStyle
        """
        style_json = self.model_dump_json()
        style_dict = json.loads(style_json)
        for a in args:
            if not isinstance(a, dict):
                raise TypeError("Style overrides must be dictionary types.")
            merge_dict(style_dict, a)
        return PlotStyle.parse_obj(style_dict)

    def has_gradient_background(self):
        return isinstance(self.background_color, list)
