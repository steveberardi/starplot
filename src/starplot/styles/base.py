import json
from enum import Enum
from pathlib import Path
from typing import Optional

import yaml

from pydantic import BaseModel
from pydantic.color import Color
from pydantic.functional_serializers import PlainSerializer
from typing_extensions import Annotated

from starplot.data.dsos import DsoType
from starplot.styles.helpers import merge_dict

ColorStr = Annotated[
    Color,
    PlainSerializer(
        lambda c: c.as_hex() if c and c != "none" else None, return_type=str
    ),
]


FONT_SCALE = 2

HERE = Path(__file__).resolve().parent


class BaseStyle(BaseModel):
    class Config:
        use_enum_values = True
        extra = "forbid"


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

    CIRCLE = "circle"
    """\u25CF"""

    SQUARE = "square"
    """\u25A0"""

    SQUARE_STRIPES_DIAGONAL = "square_stripes_diagonal"
    """\u25A8"""

    # SQUARE_CROSSHAIR = "square_crosshair"
    # """\u2BD0"""

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

    CIRCLE_DOTTED_EDGE = "circle_dotted_edge"
    """\u25CC"""

    COMET = "comet"
    """\u2604"""

    STAR_8 = "star_8"
    """\u2734"""

    def as_matplot(self) -> str:
        """Returns the matplotlib value of this marker"""
        return {
            MarkerSymbolEnum.POINT: ".",
            MarkerSymbolEnum.CIRCLE: "o",
            MarkerSymbolEnum.SQUARE: "s",
            MarkerSymbolEnum.SQUARE_STRIPES_DIAGONAL: "$\u25A8$",
            MarkerSymbolEnum.STAR: "*",
            MarkerSymbolEnum.SUN: "$\u263C$",
            MarkerSymbolEnum.DIAMOND: "D",
            MarkerSymbolEnum.TRIANGLE: "^",
            MarkerSymbolEnum.CIRCLE_PLUS: "$\u2295$",
            MarkerSymbolEnum.CIRCLE_CROSS: "$\u1AA0$",
            MarkerSymbolEnum.CIRCLE_DOTTED_EDGE: "$\u25CC$",
            MarkerSymbolEnum.COMET: "$\u2604$",
            MarkerSymbolEnum.STAR_8: "$\u2734$",
        }.get(self.value)


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

        return style


class MarkerStyle(BaseStyle):
    """
    Styling properties for markers.

    ???- tip "Example Usage"
        Creates a style for a red triangle marker:
        ```python
        m = MarkerStyle(
            color="#b13737",
            symbol="triangle",
            size=8,
            fill="full",
            alpha=1.0,
            zorder=100,
        )
        ```
    """

    color: Optional[ColorStr] = ColorStr("#000")
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

    @property
    def symbol_matplot(self) -> str:
        return MarkerSymbolEnum(self.symbol).as_matplot()

    def matplot_kwargs(self, size_multiplier: float = 1.0) -> dict:
        return dict(
            color=self.color.as_hex() if self.color else "none",
            markeredgecolor=self.edge_color.as_hex() if self.edge_color else "none",
            marker=MarkerSymbolEnum(self.symbol).as_matplot(),
            markersize=self.size * size_multiplier * FONT_SCALE,
            fillstyle=self.fill,
            alpha=self.alpha,
            zorder=self.zorder,
        )

    def to_polygon_style(self):
        return PolygonStyle(
            fill_color=self.color.as_hex() if self.color else None,
            edge_color=self.edge_color.as_hex() if self.edge_color else None,
            alpha=self.alpha,
            zorder=self.zorder,
        )


class LineStyle(BaseStyle):
    """
    Styling properties for lines.

    ???- tip "Example Usage"
        Creates a style for a dashed green line:
        ```python
        ls = LineStyle(
            width=2,
            color="#6ba832",
            style="dashed",
            alpha=0.2,
            zorder=-10,
        )
        ```
    """

    width: float = 2
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

    ???- tip "Example Usage"
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

    def matplot_kwargs(self, size_multiplier: float = 1.0) -> dict:
        styles = dict(
            edgecolor=self.edge_color.as_hex() if self.edge_color else "none",
            facecolor=self.fill_color.as_hex() if self.fill_color else "none",
            fill=True if self.fill_color else False,
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

    ???- tip "Example Usage"
        Creates a style for a bold blue label:
        ```python
        ls = LabelStyle(
                font_color="blue",
                font_weight="bold",
                zorder=1,
        )
        ```
    """

    anchor_point: AnchorPointEnum = AnchorPointEnum.BOTTOM_RIGHT
    """Anchor point of label"""

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

    offset_x: int = 0
    """Horizontal offset of the label, in pixels. Negative values supported."""

    offset_y: int = 0
    """Vertical offset of the label, in pixels. Negative values supported."""

    zorder: int = 101
    """Zorder of the label"""

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

        style.update(AnchorPointEnum(self.anchor_point).as_matplot())

        return style


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

    symbol_size: int = 16
    """Relative size of symbols in the legend"""

    symbol_padding: float = 0.2
    """Padding between each symbol and its label"""

    border_padding: float = 1.28
    """Padding around legend border"""

    font_size: int = 9
    """Relative font size of the legend labels"""

    font_color: ColorStr = ColorStr("#000")
    """Font color for legend labels"""

    zorder: int = 2_000
    """Zorder of the legend"""

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
    """Background color of the map region"""

    figure_background_color: ColorStr = ColorStr("#fff")

    text_border_width: int = 2
    text_offset_x: float = 0.005
    text_offset_y: float = 0.005

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
        zorder=1,
        line_spacing=48,
        anchor_point=AnchorPointEnum.BOTTOM_CENTER,
    )
    """Styling for info text (only applies to zenith and optic plots)"""

    # Info text
    info_text: LabelStyle = LabelStyle(
        font_size=10,
        zorder=1,
        font_family="monospace",
        line_spacing=2,
        anchor_point=AnchorPointEnum.BOTTOM_CENTER,
    )
    """Styling for info text (only applies to zenith and optic plots)"""

    # Stars
    star: ObjectStyle = ObjectStyle(
        marker=MarkerStyle(fill=FillStyleEnum.FULL, zorder=1, size=20, edge_color=None),
        label=LabelStyle(font_size=9, font_weight=FontWeightEnum.BOLD, zorder=400),
    )
    """Styling for stars *(see [`ObjectStyle`][starplot.styles.ObjectStyle])*"""

    bayer_labels: LabelStyle = LabelStyle(
        font_size=7,
        font_weight=FontWeightEnum.LIGHT,
        zorder=1,
        anchor_point=AnchorPointEnum.TOP_LEFT,
    )
    """Styling for Bayer labels of stars"""

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
            alpha=1,
            zorder=100,
        ),
        label=LabelStyle(
            font_size=8,
            font_weight=FontWeightEnum.BOLD,
        ),
    )
    """Styling for the moon"""

    sun: ObjectStyle = ObjectStyle(
        marker=MarkerStyle(
            symbol=MarkerSymbolEnum.SUN,
            size=14,
            fill=FillStyleEnum.FULL,
            color="#000",
            zorder=90,
        ),
        label=LabelStyle(
            font_size=8,
            font_weight=FontWeightEnum.BOLD,
        ),
    )
    """Styling for the Sun"""

    # Deep Sky Objects (DSOs)
    dso_open_cluster: ObjectStyle = ObjectStyle(
        marker=MarkerStyle(
            symbol=MarkerSymbolEnum.CIRCLE,
            size=6,
            fill=FillStyleEnum.FULL,
        ),
        label=LabelStyle(
            font_size=6,
            font_weight=FontWeightEnum.LIGHT,
        ),
    )
    """Styling for open star clusters"""

    dso_association_stars: ObjectStyle = ObjectStyle(
        marker=MarkerStyle(
            symbol=MarkerSymbolEnum.CIRCLE,
            size=6,
            fill=FillStyleEnum.FULL,
        ),
        label=LabelStyle(
            font_size=6,
            font_weight=FontWeightEnum.LIGHT,
        ),
    )
    """Styling for associations of stars"""

    dso_globular_cluster: ObjectStyle = ObjectStyle(
        marker=MarkerStyle(
            symbol=MarkerSymbolEnum.CIRCLE,
            size=6,
            fill=FillStyleEnum.FULL,
            color="#555",
            alpha=0.8,
        ),
        label=LabelStyle(font_size=6),
    )
    """Styling for globular star clusters"""

    dso_galaxy: ObjectStyle = ObjectStyle(
        marker=MarkerStyle(
            symbol=MarkerSymbolEnum.CIRCLE, size=6, fill=FillStyleEnum.FULL
        ),
        label=LabelStyle(font_size=6),
    )
    """Styling for galaxies"""

    dso_nebula: ObjectStyle = ObjectStyle(
        marker=MarkerStyle(
            symbol=MarkerSymbolEnum.SQUARE, size=6, fill=FillStyleEnum.FULL
        ),
        label=LabelStyle(font_size=6),
    )
    """Styling for nebulas"""

    dso_double_star: ObjectStyle = ObjectStyle(
        marker=MarkerStyle(
            symbol=MarkerSymbolEnum.CIRCLE, size=6, fill=FillStyleEnum.TOP
        ),
        label=LabelStyle(font_size=6),
    )
    """Styling for double stars"""

    dso_dark_nebula: ObjectStyle = ObjectStyle(
        marker=MarkerStyle(
            symbol=MarkerSymbolEnum.SQUARE,
            size=6,
            fill=FillStyleEnum.TOP,
            color="#000",
        ),
        label=LabelStyle(font_size=6),
    )
    """Styling for dark nebulas"""

    dso_hii_ionized_region: ObjectStyle = ObjectStyle(
        marker=MarkerStyle(
            symbol=MarkerSymbolEnum.SQUARE,
            size=6,
            fill=FillStyleEnum.TOP,
            color="#000",
        ),
        label=LabelStyle(font_size=6),
    )
    """Styling for HII Ionized regions"""

    dso_supernova_remnant: ObjectStyle = ObjectStyle(
        marker=MarkerStyle(
            symbol=MarkerSymbolEnum.SQUARE,
            size=6,
            fill=FillStyleEnum.TOP,
            color="#000",
        ),
        label=LabelStyle(font_size=6),
    )
    """Styling for supernova remnants"""

    dso_nova_star: ObjectStyle = ObjectStyle(
        marker=MarkerStyle(
            symbol=MarkerSymbolEnum.SQUARE,
            size=6,
            fill=FillStyleEnum.TOP,
            color="#000",
        ),
        label=LabelStyle(font_size=6),
    )
    """Styling for nova stars"""

    dso_nonexistant: ObjectStyle = ObjectStyle(
        marker=MarkerStyle(
            symbol=MarkerSymbolEnum.SQUARE,
            size=6,
            fill=FillStyleEnum.TOP,
            color="#000",
        ),
        label=LabelStyle(font_size=6),
    )
    """Styling for 'nonexistent' (as designated by OpenNGC) deep sky objects"""

    dso_unknown: ObjectStyle = ObjectStyle(
        marker=MarkerStyle(
            symbol=MarkerSymbolEnum.SQUARE,
            size=6,
            fill=FillStyleEnum.TOP,
            color="#000",
        ),
        label=LabelStyle(font_size=6),
    )
    """Styling for 'unknown' (as designated by OpenNGC) types of deep sky objects"""

    dso_duplicate: ObjectStyle = ObjectStyle(
        marker=MarkerStyle(
            symbol=MarkerSymbolEnum.SQUARE,
            size=6,
            fill=FillStyleEnum.TOP,
            color="#000",
        ),
        label=LabelStyle(font_size=6),
    )
    """Styling for 'duplicate record' (as designated by OpenNGC) types of deep sky objects"""

    # Constellations
    constellation: PathStyle = PathStyle(
        line=LineStyle(color="#c8c8c8"),
        label=LabelStyle(
            font_size=7,
            font_weight=FontWeightEnum.LIGHT,
            zorder=400,
            anchor_point=AnchorPointEnum.TOP_RIGHT,
        ),
    )
    """Styling for constellation lines and labels (only applies to map plots)"""

    constellation_borders: LineStyle = LineStyle(
        color="#000", width=2, style=LineStyleEnum.DASHED, alpha=0.2, zorder=-100
    )
    """Styling for constellation borders (only applies to map plots)"""

    # Milky Way
    milky_way: PolygonStyle = PolygonStyle(
        color="#d9d9d9",
        alpha=0.36,
        edge_width=0,
        zorder=-1_000,
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
            zorder=-1_000,
        ),
        label=LabelStyle(
            font_size=9,
            font_color="#000",
            font_weight=FontWeightEnum.LIGHT,
            font_alpha=1,
            anchor_point=AnchorPointEnum.BOTTOM_CENTER,
        ),
    )
    """Styling for gridlines (including Right Ascension / Declination labels). *Only applies to map plots*."""

    # Ecliptic
    ecliptic: PathStyle = PathStyle(
        line=LineStyle(
            color="#777",
            width=2,
            style=LineStyleEnum.DOTTED,
            dash_capstyle=DashCapStyleEnum.ROUND,
            alpha=0.8,
            zorder=-20,
        ),
        label=LabelStyle(
            font_size=6,
            font_color="#777",
            font_weight=FontWeightEnum.LIGHT,
            font_alpha=1,
            zorder=-20,
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
            zorder=-20,
        ),
        label=LabelStyle(
            font_size=6,
            font_color="#999",
            font_weight=FontWeightEnum.LIGHT,
            font_alpha=0.65,
            zorder=-20,
        ),
    )
    """Styling for the Celestial Equator"""

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
            DsoType.PLANETARY_NEBULA: self.dso_nebula,
            DsoType.EMISSION_NEBULA: self.dso_nebula,
            DsoType.STAR_CLUSTER_NEBULA: self.dso_nebula,
            DsoType.REFLECTION_NEBULA: self.dso_nebula,
            # Stars ----------
            DsoType.STAR: None,
            DsoType.DOUBLE_STAR: self.dso_double_star,
            DsoType.ASSOCIATION_OF_STARS: self.dso_association_stars,
            # Others (hidden by default style)
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
