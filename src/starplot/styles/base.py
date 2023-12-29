import json
from enum import Enum
from pathlib import Path
from typing import Optional

import yaml

from pydantic import BaseModel
from pydantic.color import Color
from pydantic.functional_serializers import PlainSerializer
from typing_extensions import Annotated


ColorStr = Annotated[
    Color, PlainSerializer(lambda c: c.as_hex() if c else None, return_type=str)
]


FONT_SCALE = 2

HERE = Path(__file__).resolve().parent


def merge_dict(dict_1: dict, dict_2: dict) -> None:
    """

    Args:
        dict_1: Base dictionary to merge into
        dict_2: Dictionary to merge into the base (dict_1)

    Returns:
        None (dict_1 is modified directly)
    """
    for k in dict_2.keys():
        if k in dict_1 and isinstance(dict_1[k], dict) and isinstance(dict_2[k], dict):
            merge_dict(dict_1[k], dict_2[k])
        else:
            dict_1[k] = dict_2[k]


class BaseStyle(BaseModel):
    class Config:
        use_enum_values = True


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


class MarkerStyle(BaseStyle):
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

    edge_color: Optional[ColorStr] = ColorStr("#000")
    """Edge color of marker. Can be a hex, rgb, hsl, or word string."""

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
            markeredgecolor=self.edge_color.as_hex() if self.edge_color else "none",
            marker=self.symbol,
            markersize=self.size * size_multiplier * FONT_SCALE,
            fillstyle=self.fill,
            alpha=self.alpha,
            zorder=self.zorder,
        )


class LineStyle(BaseStyle):
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

    dash_capstyle: DashCapStyleEnum = DashCapStyleEnum.PROJECTING
    """Style of dash endpoints"""

    alpha: float = 1.0
    """Alpha value (controls transparency)"""

    zorder: int = -1
    """Zorder of the line"""

    visible: bool = True
    """If True, the line will be plotted"""

    def matplot_kwargs(self, size_multiplier: float = 1.0) -> dict:
        result = dict(
            color=self.color.as_hex(),
            linestyle=self.style,
            linewidth=self.width * size_multiplier,
            # dash_capstyle=self.dash_capstyle,
            alpha=self.alpha,
            zorder=self.zorder,
        )
        return result


class PolygonStyle(BaseStyle):
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

    color: Optional[ColorStr] = None
    """If specified, this will be the fill color AND edge color of the polygon"""

    edge_color: Optional[ColorStr] = None
    """Edge color of the polygon"""

    fill_color: Optional[ColorStr] = None
    """Fill color of the polygon"""

    line_style: LineStyleEnum = LineStyleEnum.SOLID
    """Edge line style"""

    alpha: float = 1.0
    """Alpha value (controls transparency)"""

    zorder: int = -1
    """Zorder of the polygon"""

    visible: bool = True
    """If True, the polygon will be plotted"""

    def matplot_kwargs(self, size_multiplier: float = 1.0) -> dict:
        styles = dict(
            edgecolor=self.edge_color.as_hex() if self.edge_color else "none",
            facecolor=self.fill_color.as_hex() if self.fill_color else "none",
            linewidth=self.edge_width * size_multiplier,
            linestyle=self.line_style,
            alpha=self.alpha,
            zorder=self.zorder,
        )
        if self.color:
            styles["color"] = self.color.as_hex()

        return styles


class LabelStyle(BaseStyle):
    """
    Styling properties for a label.

    Example Usage:
        Creates a style for a bold blue label:
        ```python
        ls = LabelStyle(
                font_color="blue",
                font_weight=FontWeightEnum.BOLD,
                zorder=1,
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

    font_family: Optional[str] = None
    """Font family (e.g. 'monospace', 'sans-serif', 'serif', etc)"""

    line_spacing: Optional[int] = None
    """Spacing between lines of text"""

    zorder: int = 1
    """Zorder of the label"""

    visible: bool = True
    """If True, the label will be plotted"""

    def matplot_kwargs(self, size_multiplier: float = 1.0) -> dict:
        style = dict(
            color=self.font_color.as_hex(),
            fontsize=self.font_size * size_multiplier * FONT_SCALE,
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

        return style


class ObjectStyle(BaseStyle):
    """Defines the style for a SkyObject"""

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

    symbol_padding: float = 0.2
    """Padding between each symbol and its label"""

    border_padding: float = 1.28
    """Padding around legend border"""

    font_size: int = 9
    """Relative font size of the legend labels"""

    font_color: ColorStr = ColorStr("#000")
    """Font color for legend labels"""

    visible: bool = True
    """If True, the legend will be plotted"""

    def matplot_kwargs(self, size_multiplier: float = 1.0) -> dict:
        return dict(
            loc=self.location,
            ncols=self.num_columns,
            framealpha=self.background_alpha,
            fontsize=self.font_size * size_multiplier * FONT_SCALE,
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

    # Info text
    info_text: LabelStyle = LabelStyle(
        font_size=10,
        zorder=1,
        family="monospace",
        line_spacing=2,
    )
    """Styling for info text (only applies to zenith and optic plots)"""

    # Stars
    star: ObjectStyle = ObjectStyle(
        marker=MarkerStyle(fill=FillStyleEnum.FULL, zorder=1, size=10, edge_color=None),
        label=LabelStyle(font_size=9, font_weight=FontWeightEnum.BOLD, zorder=1),
    )
    """Styling for stars *(see [`ObjectStyle`][starplot.styles.ObjectStyle])*"""

    bayer_labels: LabelStyle = LabelStyle(
        font_size=8, font_weight=FontWeightEnum.LIGHT, zorder=1
    )
    """Styling for Bayer labels of stars *(see [`LabelStyle`][starplot.styles.LabelStyle])* - *only applies to map plots*"""

    planets: ObjectStyle = ObjectStyle(
        marker=MarkerStyle(
            symbol=MarkerSymbolEnum.CIRCLE,
            size=4,
            fill=FillStyleEnum.LEFT,
        ),
        label=LabelStyle(
            font_size=8,
            font_weight=FontWeightEnum.BOLD,
        ),
    )
    """Styling for planets"""

    moon: ObjectStyle = ObjectStyle(
        marker=MarkerStyle(
            symbol=MarkerSymbolEnum.CIRCLE,
            size=14,
            fill=FillStyleEnum.FULL,
            color="#c8c8c8",
            alpha=0.5,
            visible=False,
        ),
        label=LabelStyle(
            font_size=8,
            font_weight=FontWeightEnum.BOLD,
            visible=False,
        ),
    )
    """Styling for the moon"""

    # Deep Sky Objects (DSOs)
    dso: ObjectStyle = ObjectStyle(
        marker=MarkerStyle(
            symbol=MarkerSymbolEnum.TRIANGLE, size=4, fill=FillStyleEnum.FULL
        ),
        label=LabelStyle(
            font_size=8,
            font_weight=FontWeightEnum.LIGHT,
        ),
    )
    """Styling for deep sky objects (DSOs)"""

    dso_open_cluster: ObjectStyle = ObjectStyle(
        marker=MarkerStyle(
            symbol=MarkerSymbolEnum.CIRCLE,
            size=6,
            fill=FillStyleEnum.FULL,
        ),
        label=LabelStyle(
            font_size=8,
            font_weight=FontWeightEnum.LIGHT,
            visible=False,
        ),
    )
    """Styling for open star clusters"""

    dso_globular_cluster: ObjectStyle = ObjectStyle(
        marker=MarkerStyle(
            symbol=MarkerSymbolEnum.CIRCLE,
            size=6,
            fill=FillStyleEnum.FULL,
            color="#555",
            alpha=0.8,
        ),
        label=LabelStyle(font_size=8, visible=False),
    )
    """Styling for globular star clusters"""

    dso_galaxy: ObjectStyle = ObjectStyle(
        marker=MarkerStyle(
            symbol=MarkerSymbolEnum.CIRCLE, size=6, fill=FillStyleEnum.FULL
        ),
        label=LabelStyle(font_size=8, visible=False),
    )
    """Styling for galaxies"""

    dso_nebula: ObjectStyle = ObjectStyle(
        marker=MarkerStyle(
            symbol=MarkerSymbolEnum.SQUARE, size=6, fill=FillStyleEnum.FULL
        ),
        label=LabelStyle(font_size=8, visible=False),
    )
    """Styling for nebulas"""

    dso_double_star: ObjectStyle = ObjectStyle(
        marker=MarkerStyle(
            symbol=MarkerSymbolEnum.CIRCLE, size=6, fill=FillStyleEnum.TOP
        ),
        label=LabelStyle(font_size=8, visible=False),
    )
    """Styling for double stars"""

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

    # Legend
    legend: LegendStyle = LegendStyle()
    """Styling for legend - *(see [`LegendStyle`][starplot.styles.LegendStyle])* """

    # Gridlines
    gridlines: PathStyle = PathStyle(
        line=LineStyle(
            color="#888",
            width=1,
            style=LineStyleEnum.SOLID,
            alpha=0.8,
            zorder=-10_000,
        ),
        label=LabelStyle(
            font_size=11,
            font_color="#000",
            font_weight=FontWeightEnum.LIGHT,
            font_alpha=1,
        ),
    )
    """Styling for gridlines (including Right Ascension / Declination labels). *Only applies to map plots*."""

    # Tick marks
    tick_marks: LabelStyle = LabelStyle(
        font_size=5,
        font_color="#000",
        font_alpha=1,
        zorder=-100,
    )
    """Styling for tick marks on map plots."""

    # Ecliptic
    ecliptic: PathStyle = PathStyle(
        line=LineStyle(
            color="#777",
            width=1,
            style=LineStyleEnum.DOTTED,
            dash_capstyle=DashCapStyleEnum.ROUND,
            alpha=0.75,
            zorder=-20,
        ),
        label=LabelStyle(
            font_size=4,
            font_color="#777",
            font_weight=FontWeightEnum.LIGHT,
            font_alpha=1,
        ),
    )
    """Styling for the Ecliptic"""

    # Celestial Equator
    celestial_equator: PathStyle = PathStyle(
        line=LineStyle(
            color="#999",
            width=2,
            style=LineStyleEnum.DASHED_DOTS,
            alpha=0.65,
            zorder=-1024,
        ),
        label=LabelStyle(
            font_size=6,
            font_color="#999",
            font_weight=FontWeightEnum.LIGHT,
            font_alpha=0.65,
        ),
    )
    """Styling for the Celestial Equator"""

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
            return PlotStyle().extend(**style)

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

        Example Usage:
            Create an extension of the default style with map optimizations, light blue color scheme,
            and hide the constellation borders and Milky Way:

            ```python

            new_style = PlotStyle().extend(
                styles.extensions.MAP,
                styles.extensions.BLUE_LIGHT,
                {
                    "constellation_borders": {"visible": False},
                    "milky_way": {"visible": False},
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
