import json

import yaml

from starplot.models.dso import DsoType
from starplot.styles.base import BaseStyle
from starplot.styles.constants import (
    AnchorPointEnum,
    CapStyleEnum,
    FontWeightEnum,
    LineStyleEnum,
    MarkerSymbolEnum,
    ZOrderEnum,
)
from starplot.styles.elements import (
    ArrowStyle,
    AxesStyle,
    FigureStyle,
    LabelStyle,
    LegendStyle,
    LineStyle,
    MarkerStyle,
    ObjectStyle,
    PathStyle,
    PolygonStyle,
    TableStyle,
    TitleStyle,
)
from starplot.styles.helpers import merge_dict
from starplot.styles.types import ColorStr


class PlotStyle(BaseStyle):
    """
    Defines the styling for a plot
    """

    axes: AxesStyle = AxesStyle()
    """Styling for the axes of the plot, which is where the map is plotted."""

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
        font_size=85,
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
            size=20,
            edge_color=None,
        ),
        label=LabelStyle(
            font_size=40,
            font_weight=FontWeightEnum.BOLD,
            zorder=ZOrderEnum.LAYER_3 + 2,
            offset_x="auto",
            offset_y="auto",
        ),
    )
    """Styling for stars *(see [`ObjectStyle`][starplot.styles.ObjectStyle])*"""

    bayer_labels: LabelStyle = LabelStyle(
        font_size=36,
        font_weight=FontWeightEnum.LIGHT,
        font_name="GFS Didot",
        zorder=ZOrderEnum.LAYER_4,
        anchor_point=AnchorPointEnum.TOP_LEFT,
        offset_x="auto",
        offset_y="auto",
    )
    """Styling for Bayer labels of stars"""

    flamsteed_labels: LabelStyle = LabelStyle(
        font_size=26,
        font_weight=FontWeightEnum.LIGHT,
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
            font_size=32,
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
            font_size=32,
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
            font_size=32,
            font_weight=FontWeightEnum.BOLD,
        ),
    )
    """Styling for the Sun"""

    # Deep Sky Objects (DSOs)
    dso_open_cluster: ObjectStyle = ObjectStyle(
        marker=MarkerStyle(
            symbol=MarkerSymbolEnum.CIRCLE,
            line_style=(1, 2),
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
            line_style=(1, 2),
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
        width=2.5,
        style=(3, 6),
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
            style=(2, 6),
            cap_style=CapStyleEnum.ROUND,
            alpha=1,
            zorder=ZOrderEnum.LAYER_3 - 1,
        ),
        label=LabelStyle(
            font_size=30,
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
            font_size=30,
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
            font_size=30,
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
            style=LineStyleEnum.SOLID,
            cap_style=CapStyleEnum.ROUND,
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
        line_style=(2, 3),
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
