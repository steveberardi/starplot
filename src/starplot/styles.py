import json
from enum import Enum
from typing import Optional

from typing_extensions import Annotated

import yaml

from pydantic import BaseModel
from pydantic.color import Color
from pydantic.functional_serializers import PlainSerializer

ColorStr = Annotated[Color, PlainSerializer(lambda c: c.as_hex(), return_type=str)]


FONT_SCALE = 2


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

    POINT = "."
    CIRCLE = "o"
    SQUARE = "s"
    STAR = "*"
    DIAMOND = "D"
    TRIANGLE = "^"


class LineStyleEnum(str, Enum):
    SOLID = "solid"
    DASHED = "dashed"
    DASHED_DOTS = "dashdot"
    DOTTED = "dotted"


class MarkerStyle(BaseModel):
    """
    Styling properties for markers.

    Example Usage:
        Creates a style for a red triangle marker:
        ```python
        m = MarkerStyle(
            color="#b13737",
            symbol=MarkerStyleSymbolEnum.TRIANGLE,
            size=8,
            fill=FillStyleEnum.FULL,
            alpha=1.0,
            visible=True,
            zorder=100,
        )
        ```
    """

    color: ColorStr = ColorStr("#000")
    """Fill color of marker. Can be a hex, rgb, hsl, or word string."""

    symbol: MarkerSymbolEnum = MarkerSymbolEnum.POINT
    """Symbol for marker"""

    size: int = 4
    """Relative size of marker"""

    fill: FillStyleEnum = FillStyleEnum.NONE
    """Fill style of marker"""

    alpha: float = 1.0
    """Alpha value (controls transparency)"""

    zorder: int = -1
    """Zorder of marker"""

    visible: bool = True
    """If true, the marker will be plotted"""

    def matplot_kwargs(self, size_multiplier: float = 1.0) -> dict:
        return dict(
            color=self.color.as_hex(),
            marker=self.symbol,
            markersize=self.size * size_multiplier * FONT_SCALE,
            fillstyle=self.fill,
            alpha=self.alpha,
            zorder=self.zorder,
        )


class LineStyle(BaseModel):
    """
    Styling properties for lines.

    Example Usage:
        Creates a style for a dashed green line:
        ```python
        ls = LineStyle(
            width=2,
            color="#6ba832",
            style=LineStyleEnum.DASHED,
            alpha=0.2,
            zorder=-10,
        )
        ```
    """

    width: int = 2
    """Width of line"""

    color: ColorStr = ColorStr("#000")
    """Color of the line. Can be a hex, rgb, hsl, or word string."""

    style: LineStyleEnum = LineStyleEnum.SOLID
    """Style of the line (e.g. solid, dashed, etc)."""

    alpha: float = 1.0
    """Alpha value (controls transparency)"""

    zorder: int = -1
    """Zorder of the line"""

    visible: bool = True
    """If True, the line will be plotted"""

    def matplot_kwargs(self, size_multiplier: float = 1.0) -> dict:
        return dict(
            colors=self.color.as_hex(),
            linestyle=self.style,
            linewidths=self.width * size_multiplier,
            alpha=self.alpha,
            zorder=self.zorder,
        )


class PolygonStyle(BaseModel):
    """
    Styling properties for polygons.

    Example Usage:
        Creates a style for a partially transparent blue polygon:
        ```python
        ps = PolygonStyle(
                color="#d9d9d9",
                alpha=0.36,
                edge_width=0,
                zorder=-10000,
        )
        ```
    """

    edge_width: int = 1
    """Width of the polygon's edge"""

    color: ColorStr = ColorStr("#000")
    """Fill color of the polygon"""

    alpha: float = 1.0
    """Alpha value (controls transparency)"""

    zorder: int = -1
    """Zorder of the polygon"""

    visible: bool = True
    """If True, the polygon will be plotted"""

    def matplot_kwargs(self, size_multiplier: float = 1.0) -> dict:
        return dict(
            color=self.color.as_hex(),
            linewidth=self.edge_width * size_multiplier,
            alpha=self.alpha,
            zorder=self.zorder,
        )


class LabelStyle(BaseModel):
    """
    Styling properties for a label.

    Example Usage:
        Creates a style for a partially transparent blue polygon:
        ```python
        ps = PolygonStyle(
                color="#d9d9d9",
                alpha=0.36,
                edge_width=0,
                zorder=-10000,
        )
        ```
    """

    font_size: int = 8
    """Relative font size of the label"""

    font_weight: FontWeightEnum = FontWeightEnum.NORMAL
    """Font weight (e.g. normal, bold, ultra bold, etc)"""

    font_color: ColorStr = ColorStr("#000")
    """Font's color"""

    font_alpha: float = 1
    """Font's alpha (transparency)"""

    font_style: FontStyleEnum = FontStyleEnum.NORMAL
    """Style of the label (e.g. normal, italic, etc)"""

    font_name: Optional[str] = None
    """Name of the font to use"""

    zorder: int = 1
    """Zorder of the label"""

    visible: bool = True
    """If True, the label will be plotted"""

    def matplot_kwargs(self, size_multiplier: float = 1.0) -> dict:
        return dict(
            color=self.font_color.as_hex(),
            fontsize=self.font_size * size_multiplier * FONT_SCALE,
            fontstyle=self.font_style,
            fontname=self.font_name,
            weight=self.font_weight,
            alpha=self.font_alpha,
            zorder=self.zorder,
        )


class ObjectStyle(BaseModel):
    """Defines the style for a SkyObject"""

    marker: MarkerStyle = MarkerStyle()
    """Style for the object's marker (see [MarkerStyle][starplot.styles.MarkerStyle])"""

    label: LabelStyle = LabelStyle()
    """Style for the object's label (see [LabelStyle][starplot.styles.LabelStyle])"""


class PathStyle(BaseModel):
    """Defines the style for a path (e.g. constellation lines)"""

    line: LineStyle = LineStyle()
    """Style for the line (see [LineStyle][starplot.styles.LineStyle])"""

    label: LabelStyle = LabelStyle()
    """Style for the path's label (see [LabelStyle][starplot.styles.LabelStyle])"""


class PlotStyle(BaseModel):
    """
    Defines the styling for a plot
    """

    # Base
    background_color: ColorStr = ColorStr("#fff")
    text_border_width: int = 2
    text_offset_x: float = 0.005
    text_offset_y: float = 0.005

    # Borders
    border_font_size: int = 18
    border_font_weight: FontWeightEnum = FontWeightEnum.BOLD
    border_font_color: ColorStr = ColorStr("#000")
    border_line_color: ColorStr = ColorStr("#000")
    border_bg_color: ColorStr = ColorStr("#fff")

    # Stars
    star: ObjectStyle = ObjectStyle(
        marker=MarkerStyle(fillstyle=FillStyleEnum.FULL),
        label=LabelStyle(font_size=9, font_weight=FontWeightEnum.BOLD, zorder=1024),
    )
    """Styling for stars"""

    bayer_labels: LabelStyle = LabelStyle(
        font_size=8, font_weight=FontWeightEnum.LIGHT, zorder=1024
    )
    """Styling for Bayer labels of stars (only applies to map plots)"""

    # Deep Sky Objects (DSOs)
    dso: ObjectStyle = ObjectStyle(
        marker=MarkerStyle(
            symbol=MarkerSymbolEnum.TRIANGLE, size=4, fillstyle=FillStyleEnum.FULL
        ),
        label=LabelStyle(font_size=8),
    )
    """Styling for deep sky objects (DSOs)"""

    # Constellations
    constellation: PathStyle = PathStyle(
        line=LineStyle(color="#c8c8c8"),
        label=LabelStyle(font_size=7, font_weight=FontWeightEnum.LIGHT),
    )
    """Styling for constellations"""

    constellation_borders: LineStyle = LineStyle(
        color="#000", width=2, style=LineStyleEnum.DASHED, alpha=0.2, zorder=-100
    )
    """Styling for constellation borders (only applies to map plots)"""

    # Milky Way
    milky_way: PolygonStyle = PolygonStyle(
        color="#d9d9d9",
        alpha=0.36,
        edge_width=0,
        zorder=-10000,
    )
    """Styling for the Milky Way (only applies to map plots)"""

    @staticmethod
    def load_from_file(filename: str):
        """
        Load a style from a YAML file

        Args:
            filename: Filename of style file
        """
        with open(filename, "r") as sfile:
            style = yaml.safe_load(sfile)
            return PlotStyle.parse_obj(style)

    def dump_to_file(self, filename: str):
        """
        Save the style to a YAML file

        Args:
            filename: Filename of style file
        """
        with open(filename, "w") as outfile:
            style_json = self.model_dump_json()
            style_yaml = yaml.dump(json.loads(style_json))
            outfile.write(style_yaml)

    def extend(self, updates: dict) -> "PlotStyle":
        """
        Creates a new style with the provided updates

        Args:
            updates: Dictionary of updates to the style
        """
        style_json = self.model_dump_json()
        style_dict = json.loads(style_json)
        style_dict.update(updates)
        return PlotStyle.parse_obj(style_dict)


GRAYSCALE = PlotStyle()

BLUE = PlotStyle(
    background_color="#f1f6ff",
    # Borders
    border_font_color="#f1f6ff",
    border_line_color="#2f4358",
    border_bg_color="#7997b9",
    # Constellations
    constellation=PathStyle(
        line=LineStyle(width=3, color="#6ba832", alpha=0.2),
        label=LabelStyle(font_size=7, font_weight=FontWeightEnum.LIGHT),
    ),
    milky_way=PolygonStyle(
        color="#94c5e3",
        alpha=0.16,
        edge_width=0,
        zorder=-10000,
    ),
)

RED = PlotStyle(
    background_color="#ffd0d0",
    # Borders
    border_font_color="#7a0000",
    border_line_color="#7a0000",
    border_bg_color="#ff8e8e",
    # Stars
    star=ObjectStyle(
        marker=MarkerStyle(color="#7a0000"),
        label=LabelStyle(font_color="#7a0000"),
    ),
    # DSOs
    dso=ObjectStyle(
        marker=MarkerStyle(
            color="#7a0000",
            symbol=MarkerSymbolEnum.SQUARE,
            size=4,
            fill=FillStyleEnum.FULL,
        ),
        label=LabelStyle(font_color="#7a0000"),
    ),
    # Constellations
    constellation=PathStyle(
        line=LineStyle(width=3, color="#ff8e8e", alpha=0.2),
        label=LabelStyle(
            font_size=7, font_weight=FontWeightEnum.LIGHT, font_color="#7a0000"
        ),
    ),
)

CHALK = PlotStyle(
    background_color="#4c566a",
    # Borders
    border_font_color="#a3be8c",
    border_line_color="#a3be8c",
    border_bg_color="#2e3440",
    # Stars
    star=ObjectStyle(
        marker=MarkerStyle(color="#88c0d0"),
        label=LabelStyle(
            font_size=9, font_color="#88c0d0", font_weight=FontWeightEnum.BOLD
        ),
    ),
    # DSOs
    dso=ObjectStyle(
        marker=MarkerStyle(
            color="rgb(230, 204, 147)",
            symbol=MarkerSymbolEnum.TRIANGLE,
            size=4,
            fill=FillStyleEnum.FULL,
            alpha=0.46,
        ),
        label=LabelStyle(
            font_size=7,
            font_color="rgb(230, 204, 147)",
            font_weight=FontWeightEnum.LIGHT,
            font_alpha=0.6,
        ),
    ),
    # Constellations
    constellation=PathStyle(
        line=LineStyle(width=2, color="rgb(230, 204, 147)", alpha=0.36),
        label=LabelStyle(
            font_size=7,
            font_weight=FontWeightEnum.LIGHT,
            font_color="rgb(230, 204, 147)",
            font_alpha=0.6,
        ),
    ),
)

MAP_BLUE = PlotStyle(
    background_color="#fff",
    # Borders
    border_font_color="#f1f6ff",
    border_line_color="#2f4358",
    border_bg_color="#7997b9",
    star=ObjectStyle(
        marker=MarkerStyle(fillstyle=FillStyleEnum.FULL),
        label=LabelStyle(font_size=8, font_weight=FontWeightEnum.BOLD, zorder=1024),
    ),
    bayer_labels=LabelStyle(
        font_size=7, font_weight=FontWeightEnum.LIGHT, zorder=1024, alpha=0.72
    ),
    # Constellations
    constellation=PathStyle(
        line=LineStyle(width=3, color="#6ba832", alpha=0.34),
        label=LabelStyle(
            font_size=11, font_color="#c5c5c5", font_weight=FontWeightEnum.LIGHT
        ),
    ),
    # Milky Way
    milky_way=PolygonStyle(
        color="#94c5e3",
        alpha=0.16,
        edge_width=0,
        zorder=-10000,
    ),
)
