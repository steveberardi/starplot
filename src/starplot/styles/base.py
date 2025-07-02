import json

from enum import Enum
from pathlib import Path
from typing import Optional, Union, List

import yaml

from pydantic import BaseModel
from pydantic.color import Color
from pydantic.functional_serializers import PlainSerializer
from matplotlib import patheffects
from typing_extensions import Annotated

from starplot.models.dso import DsoType
from starplot.styles.helpers import merge_dict
from starplot.styles.markers import (
    ellipse,
    circle_cross,
    circle_crosshair,
    circle_line,
    circle_dot,
    circle_dotted_rings,
)


ColorStr = Annotated[
    Color,
    PlainSerializer(
        lambda c: c.as_hex() if c and c != "none" else None,
        return_type=str,
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


class FillStyleEnum(str, Enum):
    """Constants that represent the possible fill styles for markers."""

    FULL = "full"
    """Fill the marker completely"""

    LEFT = "left"
    """Fill the left half of the marker"""

    RIGHT = "right"
    """Fill the right half of the marker"""

    BOTTOM = "bottom"
    """Fill the bottom half"""

    TOP = "top"
    """Fill the top half"""

    NONE = "none"
    """Do not fill the marker. It'll still have an edge, but the inside will be transparent."""


class FontWeightEnum(str, Enum):
    """Options for font weight."""

    NORMAL = "normal"
    BOLD = "bold"
    HEAVY = "heavy"
    LIGHT = "light"
    ULTRA_BOLD = "ultrabold"
    ULTRA_LIGHT = "ultralight"


class FontStyleEnum(str, Enum):
    NORMAL = "normal"
    ITALIC = "italic"
    OBLIQUE = "oblique"


class MarkerSymbolEnum(str, Enum):
    """Options for marker symbols"""

    POINT = "point"
    """\u00B7"""

    PLUS = "plus"
    """+"""

    CIRCLE = "circle"
    """\u25CF"""

    SQUARE = "square"
    """\u25A0"""

    SQUARE_STRIPES_DIAGONAL = "square_stripes_diagonal"
    """\u25A8"""

    STAR = "star"
    """\u2605"""

    SUN = "sun"
    """\u263C"""

    DIAMOND = "diamond"
    """\u25C6"""

    TRIANGLE = "triangle"
    """\u23F6"""

    CIRCLE_PLUS = "circle_plus"
    """\u2295"""

    CIRCLE_CROSS = "circle_cross"
    """\u1AA0"""

    CIRCLE_CROSSHAIR = "circle_crosshair"
    """No preview available, but this is the standard symbol for planetary nebulae"""

    CIRCLE_DOT = "circle_dot"
    """\u29BF"""

    CIRCLE_DOTTED_EDGE = "circle_dotted_edge"
    """\u25CC"""

    CIRCLE_DOTTED_RINGS = "circle_dotted_rings"

    CIRCLE_LINE = "circle_line"
    """\u29B5  the standard symbol for double stars"""

    COMET = "comet"
    """\u2604"""

    STAR_4 = "star_4"
    """\u2726"""

    STAR_8 = "star_8"
    """\u2734"""

    ELLIPSE = "ellipse"
    """\u2B2D"""

    def as_matplot(self) -> str:
        """Returns the matplotlib value of this marker"""
        return {
            MarkerSymbolEnum.POINT: ".",
            MarkerSymbolEnum.CIRCLE: "o",
            MarkerSymbolEnum.SQUARE: "s",
            MarkerSymbolEnum.PLUS: "P",
            MarkerSymbolEnum.SQUARE_STRIPES_DIAGONAL: "$\u25A8$",
            MarkerSymbolEnum.STAR: "*",
            MarkerSymbolEnum.SUN: "$\u263C$",
            MarkerSymbolEnum.DIAMOND: "D",
            MarkerSymbolEnum.TRIANGLE: "^",
            MarkerSymbolEnum.CIRCLE_PLUS: "$\u2295$",
            MarkerSymbolEnum.CIRCLE_CROSS: circle_cross(),
            MarkerSymbolEnum.CIRCLE_CROSSHAIR: circle_crosshair(),
            MarkerSymbolEnum.CIRCLE_DOT: circle_dot(),
            MarkerSymbolEnum.CIRCLE_DOTTED_EDGE: "$\u25CC$",
            MarkerSymbolEnum.CIRCLE_DOTTED_RINGS: circle_dotted_rings(),
            MarkerSymbolEnum.CIRCLE_LINE: circle_line(),
            MarkerSymbolEnum.COMET: "$\u2604$",
            MarkerSymbolEnum.STAR_4: "$\u2726$",
            MarkerSymbolEnum.STAR_8: "$\u2734$",
            MarkerSymbolEnum.ELLIPSE: ellipse(),
        }[self.value]


class LineStyleEnum(str, Enum):
    SOLID = "solid"
    DASHED = "dashed"
    DASHED_DOTS = "dashdot"
    DOTTED = "dotted"


class DashCapStyleEnum(str, Enum):
    BUTT = "butt"
    PROJECTING = "projecting"
    ROUND = "round"


class LegendLocationEnum(str, Enum):
    """Options for the location of the map legend"""

    INSIDE_TOP = "upper center"
    INSIDE_TOP_LEFT = "upper left"
    INSIDE_TOP_RIGHT = "upper right"
    INSIDE_BOTTOM = "lower center"
    INSIDE_BOTTOM_RIGHT = "lower right"
    INSIDE_BOTTOM_LEFT = "lower left"
    OUTSIDE_TOP = "outside upper center"
    OUTSIDE_BOTTOM = "outside lower center"


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

    def as_matplot(self) -> dict:
        style = {}
        # the values below look wrong, but they're inverted because the map coords are inverted
        if self.value == AnchorPointEnum.BOTTOM_LEFT:
            style["va"] = "top"
            style["ha"] = "right"
        elif self.value == AnchorPointEnum.BOTTOM_RIGHT:
            style["va"] = "top"
            style["ha"] = "left"
        elif self.value == AnchorPointEnum.BOTTOM_CENTER:
            style["va"] = "top"
            style["ha"] = "center"
        elif self.value == AnchorPointEnum.TOP_LEFT:
            style["va"] = "bottom"
            style["ha"] = "right"
        elif self.value == AnchorPointEnum.TOP_RIGHT:
            style["va"] = "bottom"
            style["ha"] = "left"
        elif self.value == AnchorPointEnum.TOP_CENTER:
            style["va"] = "bottom"
            style["ha"] = "center"
        elif self.value == AnchorPointEnum.CENTER:
            style["va"] = "center"
            style["ha"] = "center"
        elif self.value == AnchorPointEnum.LEFT_CENTER:
            style["va"] = "center"
            style["ha"] = "right"
        elif self.value == AnchorPointEnum.RIGHT_CENTER:
            style["va"] = "center"
            style["ha"] = "left"

        return style

    @staticmethod
    def from_str(value: str) -> "AnchorPointEnum":
        options = {ap.value: ap for ap in AnchorPointEnum}
        return options.get(value)


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

    color: Optional[ColorStr] = ColorStr("#000")
    """Fill color of marker. Can be a hex, rgb, hsl, or word string."""

    edge_color: Optional[ColorStr] = ColorStr("#000")
    """Edge color of marker. Can be a hex, rgb, hsl, or word string."""

    edge_width: float = 1
    """Edge width of marker, in points. Not available for all marker symbols."""

    line_style: Union[LineStyleEnum, tuple] = LineStyleEnum.SOLID
    """Edge line style. Can be a predefined value in `LineStyleEnum` or a [Matplotlib linestyle tuple](https://matplotlib.org/stable/gallery/lines_bars_and_markers/linestyles.html)."""

    dash_capstyle: DashCapStyleEnum = DashCapStyleEnum.PROJECTING
    """Style of dash endpoints"""

    symbol: MarkerSymbolEnum = MarkerSymbolEnum.POINT
    """Symbol for marker"""

    size: float = 22
    """Size of marker in points"""

    fill: FillStyleEnum = FillStyleEnum.NONE
    """Fill style of marker"""

    alpha: float = 1.0
    """Alpha value (controls transparency)"""

    zorder: int = ZOrderEnum.LAYER_2
    """Zorder of marker"""

    @property
    def symbol_matplot(self) -> str:
        return MarkerSymbolEnum(self.symbol).as_matplot()

    def matplot_kwargs(self, scale: float = 1.0) -> dict:
        return dict(
            color=self.color.as_hex() if self.color else "none",
            markeredgecolor=self.edge_color.as_hex() if self.edge_color else "none",
            marker=MarkerSymbolEnum(self.symbol).as_matplot(),
            markersize=self.size * scale,
            fillstyle=self.fill,
            alpha=self.alpha,
            zorder=self.zorder,
        )

    def matplot_scatter_kwargs(self, scale: float = 1.0) -> dict:
        plot_kwargs = self.matplot_kwargs(scale)
        plot_kwargs["edgecolors"] = plot_kwargs.pop("markeredgecolor")

        # matplotlib's plot() function takes the marker size in points diameter
        # and the scatter() function takes it in points squared
        plot_kwargs["s"] = ((plot_kwargs.pop("markersize") / scale) ** 2) * (scale**2)

        plot_kwargs["c"] = plot_kwargs.pop("color")
        plot_kwargs["linewidths"] = self.edge_width * scale
        plot_kwargs["linestyle"] = self.line_style
        plot_kwargs["capstyle"] = self.dash_capstyle

        plot_kwargs.pop("fillstyle")

        return plot_kwargs

    def to_polygon_style(self):
        return PolygonStyle(
            fill_color=self.color.as_hex() if self.color else None,
            edge_color=self.edge_color.as_hex() if self.edge_color else None,
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

    color: ColorStr = ColorStr("#000")
    """Color of the line. Can be a hex, rgb, hsl, or word string."""

    style: Union[LineStyleEnum, tuple] = LineStyleEnum.SOLID
    """Style of the line (e.g. solid, dashed, etc). Can be a predefined value in `LineStyleEnum` or a [Matplotlib linestyle tuple](https://matplotlib.org/stable/gallery/lines_bars_and_markers/linestyles.html)."""

    dash_capstyle: DashCapStyleEnum = DashCapStyleEnum.PROJECTING
    """Style of dash endpoints"""

    alpha: float = 1.0
    """Alpha value (controls transparency)"""

    zorder: int = ZOrderEnum.LAYER_2
    """Zorder of the line"""

    edge_width: int = 0
    """Width of the line's edge in points. _If the width or color is falsey then the line will NOT be drawn with an edge._"""

    edge_color: Optional[ColorStr] = None
    """Edge color of the line. _If the width or color is falsey then the line will NOT be drawn with an edge._"""

    def matplot_kwargs(self, scale: float = 1.0) -> dict:
        line_width = self.width * scale

        result = dict(
            color=self.color.as_hex(),
            linestyle=self.style,
            linewidth=line_width,
            # dash_capstyle=self.dash_capstyle,
            alpha=self.alpha,
            zorder=self.zorder,
        )

        if self.edge_width and self.edge_color:
            result["path_effects"] = [
                patheffects.withStroke(
                    linewidth=line_width + 2 * self.edge_width * scale,
                    foreground=self.edge_color.as_hex(),
                )
            ]

        return result

    def matplot_line_collection_kwargs(self, scale: float = 1.0) -> dict:
        plot_kwargs = self.matplot_kwargs(scale)
        plot_kwargs["linewidths"] = plot_kwargs.pop("linewidth")
        plot_kwargs["colors"] = plot_kwargs.pop("color")
        return plot_kwargs


class PolygonStyle(BaseStyle):
    """
    Styling properties for polygons.
    """

    edge_width: float = 1
    """Width of the polygon's edge in points"""

    color: Optional[ColorStr] = None
    """If specified, this will be the fill color AND edge color of the polygon"""

    edge_color: Optional[ColorStr] = None
    """Edge color of the polygon"""

    fill_color: Optional[ColorStr] = None
    """Fill color of the polygon"""

    line_style: Union[LineStyleEnum, tuple] = LineStyleEnum.SOLID
    """Edge line style. Can be a predefined value in `LineStyleEnum` or a [Matplotlib linestyle tuple](https://matplotlib.org/stable/gallery/lines_bars_and_markers/linestyles.html)."""

    alpha: float = 1.0
    """Alpha value (controls transparency)"""

    zorder: int = -1
    """Zorder of the polygon"""

    def matplot_kwargs(self, scale: float = 1.0) -> dict:
        styles = dict(
            edgecolor=self.edge_color.as_hex() if self.edge_color else "none",
            facecolor=self.fill_color.as_hex() if self.fill_color else "none",
            fill=True if self.fill_color or self.color else False,
            linewidth=self.edge_width * scale,
            linestyle=self.line_style,
            alpha=self.alpha,
            zorder=self.zorder,
            capstyle="round",
        )
        if self.color:
            styles["color"] = self.color.as_hex()

        return styles

    def to_marker_style(self, symbol: MarkerSymbolEnum):
        color = self.color.as_hex() if self.color else None
        fill_color = self.fill_color.as_hex() if self.fill_color else None
        fill_style = FillStyleEnum.FULL if color or fill_color else FillStyleEnum.NONE
        return MarkerStyle(
            symbol=symbol,
            color=color or fill_color,
            fill=fill_style,
            edge_color=self.edge_color.as_hex() if self.edge_color else None,
            edge_width=self.edge_width,
            alpha=self.alpha,
            zorder=self.zorder,
            line_style=self.line_style,
        )


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

    font_family: Optional[str] = None
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

    def matplot_kwargs(self, scale: float = 1.0) -> dict:
        style = dict(
            color=self.font_color.as_hex(),
            fontsize=self.font_size * scale,
            fontstyle=self.font_style,
            fontname=self.font_name,
            weight=self.font_weight,
            alpha=self.font_alpha,
            zorder=self.zorder,
        )

        if self.font_family:
            style["family"] = self.font_family
        if self.line_spacing:
            style["linespacing"] = self.line_spacing

        if self.border_width != 0 and self.border_color is not None:
            style["path_effects"] = [
                patheffects.withStroke(
                    linewidth=self.border_width * scale,
                    foreground=self.border_color.as_hex(),
                )
            ]

        style.update(AnchorPointEnum(self.anchor_point).as_matplot())

        return style

    def offset_from_marker(self, marker_symbol, marker_size, scale: float = 1.0):
        if self.offset_x != "auto" or self.offset_y != "auto":
            return self

        new_style = self.model_copy()

        x_direction = -1 if new_style.anchor_point.endswith("left") else 1
        y_direction = -1 if new_style.anchor_point.startswith("bottom") else 1

        offset = (marker_size**0.5 / 2) / scale

        # matplotlib seems to use marker size differently depending on symbol (for scatter)
        # it is NOT strictly the area of the bounding box of the marker
        if marker_symbol in [MarkerSymbolEnum.POINT]:
            offset /= PI

        elif marker_symbol != MarkerSymbolEnum.SQUARE:
            offset /= SQR_2
            offset *= scale

        offset += 1.1

        new_style.offset_x = offset * float(x_direction)
        new_style.offset_y = offset * float(y_direction)

        return new_style


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


class LegendStyle(BaseStyle):
    """Defines the style for the map legend. *Only applies to map plots.*"""

    location: LegendLocationEnum = LegendLocationEnum.OUTSIDE_BOTTOM
    """Location of the legend, relative to the map area (inside or outside)"""

    background_color: ColorStr = ColorStr("#fff")
    """Background color of the legend box"""

    background_alpha: float = 1.0
    """Background's alpha (transparency)"""

    expand: bool = False
    """If True, the legend will be expanded to fit the full width of the map"""

    num_columns: int = 8
    """Number of columns in the legend"""

    label_padding: float = 1.6
    """Padding between legend labels"""

    symbol_size: int = 34
    """Size of symbols in the legend, in points"""

    symbol_padding: float = 0.2
    """Padding between each symbol and its label"""

    border_padding: float = 1.28
    """Padding around legend border"""

    font_size: int = 23
    """Font size of the legend labels, in points"""

    font_color: ColorStr = ColorStr("#000")
    """Font color for legend labels"""

    zorder: int = ZOrderEnum.LAYER_5
    """Zorder of the legend"""

    def matplot_kwargs(self, scale: float = 1.0) -> dict:
        return dict(
            loc=self.location,
            ncols=self.num_columns,
            framealpha=self.background_alpha,
            fontsize=self.font_size * scale,
            labelcolor=self.font_color.as_hex(),
            borderpad=self.border_padding,
            labelspacing=self.label_padding,
            handletextpad=self.symbol_padding,
            mode="expand" if self.expand else None,
            facecolor=self.background_color.as_hex(),
        )


class PlotStyle(BaseStyle):
    """
    Defines the styling for a plot
    """

    background_color: ColorStr = ColorStr("#fff")
    """Background color of the map region"""

    figure_background_color: ColorStr = ColorStr("#fff")

    text_border_width: int = 2
    """Text border (aka halos) width. This will apply to _all_ text labels on the plot. If you'd like to control these borders by object type, then set this global width to `0` and refer to the label style's `border_width` and `border_color` properties."""

    text_border_color: ColorStr = ColorStr("#fff")

    text_anchor_fallbacks: List[AnchorPointEnum] = [
        AnchorPointEnum.BOTTOM_RIGHT,
        AnchorPointEnum.TOP_LEFT,
        AnchorPointEnum.TOP_RIGHT,
        AnchorPointEnum.BOTTOM_LEFT,
        AnchorPointEnum.BOTTOM_CENTER,
        AnchorPointEnum.TOP_CENTER,
        AnchorPointEnum.RIGHT_CENTER,
        AnchorPointEnum.LEFT_CENTER,
    ]
    """If a label's preferred anchor point results in a collision, then these fallbacks will be tried in sequence until a collision-free position is found."""

    # Borders
    border_font_size: int = 18
    border_font_weight: FontWeightEnum = FontWeightEnum.BOLD
    border_font_color: ColorStr = ColorStr("#000")
    border_line_color: ColorStr = ColorStr("#000")
    border_bg_color: ColorStr = ColorStr("#fff")

    # Title
    title: LabelStyle = LabelStyle(
        font_size=20,
        font_weight=FontWeightEnum.BOLD,
        zorder=ZOrderEnum.LAYER_5,
        line_spacing=48,
        anchor_point=AnchorPointEnum.BOTTOM_CENTER,
    )
    """Styling for info text (only applies to zenith and optic plots)"""

    # Info text
    info_text: LabelStyle = LabelStyle(
        font_size=30,
        zorder=ZOrderEnum.LAYER_5,
        font_family="Inter",
        line_spacing=1.2,
        anchor_point=AnchorPointEnum.BOTTOM_CENTER,
    )
    """Styling for info text (only applies to zenith and optic plots)"""

    # Stars
    star: ObjectStyle = ObjectStyle(
        marker=MarkerStyle(
            fill=FillStyleEnum.FULL,
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
        font_weight=FontWeightEnum.LIGHT,
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
            fill=FillStyleEnum.LEFT,
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
            fill=FillStyleEnum.FULL,
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
            fill=FillStyleEnum.FULL,
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
            fill=FillStyleEnum.FULL,
            line_style=(0, (1, 2)),
            edge_width=1.3,
            zorder=ZOrderEnum.LAYER_3 - 1,
        ),
        label=LabelStyle(offset_x="auto", offset_y="auto"),
    )
    """Styling for open star clusters"""

    dso_association_stars: ObjectStyle = ObjectStyle(
        marker=MarkerStyle(
            symbol=MarkerSymbolEnum.CIRCLE,
            fill=FillStyleEnum.FULL,
            line_style=(0, (1, 2)),
            edge_width=1.3,
            zorder=ZOrderEnum.LAYER_3 - 1,
        ),
        label=LabelStyle(offset_x="auto", offset_y="auto"),
    )
    """Styling for associations of stars"""

    dso_globular_cluster: ObjectStyle = ObjectStyle(
        marker=MarkerStyle(
            symbol=MarkerSymbolEnum.CIRCLE_CROSS,
            fill=FillStyleEnum.FULL,
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
            fill=FillStyleEnum.FULL,
            zorder=ZOrderEnum.LAYER_3 - 1,
        ),
        label=LabelStyle(offset_x="auto", offset_y="auto"),
    )
    """Styling for galaxies"""

    dso_nebula: ObjectStyle = ObjectStyle(
        marker=MarkerStyle(
            symbol=MarkerSymbolEnum.SQUARE,
            fill=FillStyleEnum.FULL,
            zorder=ZOrderEnum.LAYER_3 - 1,
        ),
        label=LabelStyle(offset_x="auto", offset_y="auto"),
    )
    """Styling for nebulas"""

    dso_planetary_nebula: ObjectStyle = ObjectStyle(
        marker=MarkerStyle(
            symbol=MarkerSymbolEnum.CIRCLE_CROSSHAIR,
            fill=FillStyleEnum.FULL,
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
            fill=FillStyleEnum.TOP,
            zorder=ZOrderEnum.LAYER_3 - 1,
        ),
        label=LabelStyle(offset_x=1, offset_y=-1),
    )
    """Styling for double stars"""

    dso_dark_nebula: ObjectStyle = ObjectStyle(
        marker=MarkerStyle(
            symbol=MarkerSymbolEnum.SQUARE,
            fill=FillStyleEnum.TOP,
            color="#000",
            zorder=ZOrderEnum.LAYER_3 - 1,
        ),
        label=LabelStyle(),
    )
    """Styling for dark nebulas"""

    dso_hii_ionized_region: ObjectStyle = ObjectStyle(
        marker=MarkerStyle(
            symbol=MarkerSymbolEnum.SQUARE,
            fill=FillStyleEnum.TOP,
            color="#000",
            zorder=ZOrderEnum.LAYER_3 - 1,
        ),
        label=LabelStyle(),
    )
    """Styling for HII Ionized regions"""

    dso_supernova_remnant: ObjectStyle = ObjectStyle(
        marker=MarkerStyle(
            symbol=MarkerSymbolEnum.SQUARE,
            fill=FillStyleEnum.TOP,
            color="#000",
            zorder=ZOrderEnum.LAYER_3 - 1,
        ),
        label=LabelStyle(),
    )
    """Styling for supernova remnants"""

    dso_nova_star: ObjectStyle = ObjectStyle(
        marker=MarkerStyle(
            symbol=MarkerSymbolEnum.SQUARE,
            fill=FillStyleEnum.TOP,
            color="#000",
            zorder=ZOrderEnum.LAYER_3 - 1,
        ),
        label=LabelStyle(),
    )
    """Styling for nova stars"""

    dso_nonexistant: ObjectStyle = ObjectStyle(
        marker=MarkerStyle(
            symbol=MarkerSymbolEnum.SQUARE,
            fill=FillStyleEnum.TOP,
            color="#000",
            zorder=ZOrderEnum.LAYER_3 - 1,
        ),
        label=LabelStyle(),
    )
    """Styling for 'nonexistent' (as designated by OpenNGC) deep sky objects"""

    dso_unknown: ObjectStyle = ObjectStyle(
        marker=MarkerStyle(
            symbol=MarkerSymbolEnum.SQUARE,
            fill=FillStyleEnum.TOP,
            color="#000",
            zorder=ZOrderEnum.LAYER_3 - 1,
        ),
        label=LabelStyle(),
    )
    """Styling for 'unknown' (as designated by OpenNGC) types of deep sky objects"""

    dso_duplicate: ObjectStyle = ObjectStyle(
        marker=MarkerStyle(
            symbol=MarkerSymbolEnum.SQUARE,
            fill=FillStyleEnum.TOP,
            color="#000",
            zorder=ZOrderEnum.LAYER_3 - 1,
        ),
        label=LabelStyle(),
    )
    """Styling for 'duplicate record' (as designated by OpenNGC) types of deep sky objects"""

    constellation_lines: LineStyle = LineStyle(color="#c8c8c8")
    """Styling for constellation lines"""

    constellation_borders: LineStyle = LineStyle(
        color="#000",
        width=1.5,
        style=LineStyleEnum.DASHED,
        alpha=0.4,
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
            alpha=0.8,
            zorder=ZOrderEnum.LAYER_2,
        ),
        label=LabelStyle(
            font_size=20,
            font_color="#000",
            font_alpha=1,
            anchor_point=AnchorPointEnum.BOTTOM_CENTER,
        ),
    )
    """Styling for gridlines (including Right Ascension / Declination labels). *Only applies to map plots*."""

    # Ecliptic
    ecliptic: PathStyle = PathStyle(
        line=LineStyle(
            color="#777",
            width=3,
            style=LineStyleEnum.DOTTED,
            dash_capstyle=DashCapStyleEnum.ROUND,
            alpha=1,
            zorder=ZOrderEnum.LAYER_3 - 1,
        ),
        label=LabelStyle(
            font_size=22,
            font_color="#777",
            font_alpha=1,
            zorder=ZOrderEnum.LAYER_3,
        ),
    )
    """Styling for the Ecliptic"""

    # Celestial Equator
    celestial_equator: PathStyle = PathStyle(
        line=LineStyle(
            color="#999",
            width=3,
            style=LineStyleEnum.DASHED_DOTS,
            alpha=0.65,
            zorder=ZOrderEnum.LAYER_3,
        ),
        label=LabelStyle(
            font_size=22,
            font_color="#999",
            font_weight=FontWeightEnum.LIGHT,
            font_alpha=0.65,
            zorder=ZOrderEnum.LAYER_3,
        ),
    )
    """Styling for the Celestial Equator"""

    horizon: PathStyle = PathStyle(
        line=LineStyle(
            color="#fff",
            width=80,
            edge_width=4,
            edge_color="#000",
            style=LineStyleEnum.SOLID,
            dash_capstyle=DashCapStyleEnum.BUTT,
            alpha=1,
            zorder=ZOrderEnum.LAYER_5,
        ),
        label=LabelStyle(
            anchor_point=AnchorPointEnum.CENTER,
            font_color="#000",
            font_size=64,
            font_weight=FontWeightEnum.BOLD,
            zorder=ZOrderEnum.LAYER_5,
        ),
    )
    """Styling for the horizon"""

    zenith: ObjectStyle = ObjectStyle(
        marker=MarkerStyle(
            symbol=MarkerSymbolEnum.TRIANGLE,
            size=24,
            fill=FillStyleEnum.FULL,
            color="#000",
            alpha=0.8,
        ),
        label=LabelStyle(font_size=14, font_weight=FontWeightEnum.BOLD),
    )
    """Styling for the zenith marker"""

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
            # Stars ----------
            DsoType.STAR: self.star,
            DsoType.DOUBLE_STAR: self.dso_double_star,
            DsoType.ASSOCIATION_OF_STARS: self.dso_association_stars,
            # Others ----------
            DsoType.DARK_NEBULA: self.dso_dark_nebula,
            DsoType.HII_IONIZED_REGION: self.dso_hii_ionized_region,
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
