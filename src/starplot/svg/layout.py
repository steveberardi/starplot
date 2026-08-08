from dataclasses import dataclass, field

from starplot.svg.elements import Element, Group, SVG, Rectangle, Defs
from starplot.styles import (
    TitleStyle,
    LegendStyle,
    PathStyle,
    LegendLocationEnum,
    AlignmentEnum,
)


@dataclass
class Region:
    elements: list[tuple[int, Element]] = field(default_factory=list)
    height: int = 0
    width: int = 0

    @property
    def is_empty(self):
        return not bool(self.elements and self.height and self.width)

    def clear(self):
        self.elements = []
        self.height = 0
        self.width = 0

    def render(self, x: int, y: int) -> Group | SVG | None:
        if self.is_empty:
            return None

        sorted_by_z = sorted(self.elements, key=lambda e: e[0])
        elements = [e for _, e in sorted_by_z]
        return Group(
            children=elements,
            attrs={"transform": f"translate({x}, {y})"},
        )


@dataclass
class AxesRegion(Region):
    defs: dict[str, Element] = field(default_factory=dict)

    def render(self, x, y) -> SVG:
        axes_sorted_by_z = sorted(self.elements, key=lambda e: e[0])
        axes_elements = [e for _, e in axes_sorted_by_z]
        return SVG(
            id="axes",
            x=x,
            y=y,
            height=self.height,
            width=self.width,
            children=[
                Defs(children=self.defs.values()),
                Group(
                    id="axes",
                    attrs={
                        "clip-path": "url(#axes-clip-path)",
                    },
                    children=axes_elements,
                ),
            ],
        )


@dataclass
class LegendRegion(Region):
    location: LegendLocationEnum = LegendLocationEnum.OUTSIDE_TOP_RIGHT
    margin_x: int = 0
    margin_y: int = 0

    def render(self, x, y) -> Group:
        if self.is_empty:
            return None

        sorted_by_z = sorted(self.elements, key=lambda e: e[0])
        elements = [e for _, e in sorted_by_z]
        return Group(
            children=elements,
            attrs={"transform": f"translate({x}, {y})"},
        )


@dataclass
class TableRegion(Region):
    alignment: AlignmentEnum = AlignmentEnum.CENTER


@dataclass
class Layout:
    axes: AxesRegion = field(default_factory=AxesRegion)
    axes_border: Region = field(default_factory=Region)
    axes_footer: Region = field(default_factory=Region)
    title: Region = field(default_factory=Region)
    legend: LegendRegion = field(default_factory=LegendRegion)
    table: TableRegion = field(default_factory=TableRegion)

    def render(self, style, text_as_path: bool):
        """
        Renders each region

        This function is responsible for determining the transform() for each region
        """
        height = (
            style.figure.padding * 2
            + self.title.height
            + max(self.axes.height, self.axes_border.height)
            + self.axes_footer.height
            + self.table.height
        )
        width = style.figure.padding * 2 + max(self.axes.width, self.axes_border.width)

        if "outside" in str(self.legend.location):
            width += self.legend.width + self.legend.margin_x

        axes_x = style.figure.padding
        axes_y = style.figure.padding

        if self.legend.location in [
            LegendLocationEnum.OUTSIDE_TOP_LEFT.value,
            LegendLocationEnum.OUTSIDE_BOTTOM_LEFT.value,
        ]:
            axes_x += self.legend.width + self.legend.margin_x

        if not self.title.is_empty:
            axes_y += self.title.height

        axes_border_x = axes_x
        axes_border_y = axes_y
        border_width_x = 0
        border_width_y = 0
        if not self.axes_border.is_empty:
            border_width_x = (self.axes_border.width - self.axes.width) / 2
            border_width_y = (self.axes_border.height - self.axes.height) / 2
            axes_x += border_width_x
            axes_y += border_width_y

        elements = []
        if not self.title.is_empty:
            elements.append(self.title.render(x=0, y=style.figure.padding))

        if not self.axes_border.is_empty:
            elements.append(self.axes_border.render(x=axes_border_x, y=axes_border_y))

        if not self.table.is_empty:
            table_y = (
                axes_border_y
                + max(self.axes.height, self.axes_border.height)
                + self.axes_footer.height
            )
            axes_span = max(self.axes.width, self.axes_border.width)
            if self.table.alignment == AlignmentEnum.RIGHT:
                table_x = axes_border_x + axes_span - self.table.width
            elif self.table.alignment == AlignmentEnum.CENTER:
                table_x = axes_border_x + (axes_span - self.table.width) / 2
            else:
                table_x = axes_border_x
            elements.append(self.table.render(x=table_x, y=table_y))

        if not self.legend.is_empty:
            legend_x = 0
            legend_y = 0
            loc = self.legend.location
            if loc == LegendLocationEnum.INSIDE_TOP_LEFT:
                legend_x = axes_x + self.legend.margin_x
                legend_y = axes_y + self.legend.margin_y
            elif loc == LegendLocationEnum.INSIDE_TOP_RIGHT:
                legend_x = (
                    axes_x + self.axes.width - self.legend.width - self.legend.margin_x
                )
                legend_y = axes_y + self.legend.margin_y
            elif loc == LegendLocationEnum.INSIDE_BOTTOM_LEFT:
                legend_x = axes_x + style.margin_x
                legend_y = (
                    axes_y
                    + self.axes.height
                    - self.legend.height
                    - self.legend.margin_y
                )
            elif loc == LegendLocationEnum.INSIDE_BOTTOM_RIGHT:
                legend_x = (
                    axes_x + self.axes.width - self.legend.width - self.legend.margin_x
                )
                legend_y = (
                    axes_y
                    + self.axes.height
                    - self.legend.height
                    - self.legend.margin_y
                )
            elif loc == LegendLocationEnum.OUTSIDE_TOP_LEFT:
                legend_x = axes_border_x - self.legend.width - self.legend.margin_x
                legend_y = axes_border_y + self.legend.margin_y
            elif loc == LegendLocationEnum.OUTSIDE_BOTTOM_LEFT:
                legend_x = axes_border_x - self.legend.width - self.legend.margin_x
                legend_y = (
                    axes_border_y
                    + self.axes.height
                    - self.legend.height
                    - self.legend.margin_y
                )
            elif loc == LegendLocationEnum.OUTSIDE_BOTTOM_RIGHT:
                legend_x = (
                    axes_x + self.axes.width + border_width_x + self.legend.margin_x
                )
                legend_y = (
                    axes_border_y
                    + self.axes.height
                    + border_width_y
                    - self.legend.height
                    - self.legend.margin_y
                )
            elif loc == LegendLocationEnum.OUTSIDE_TOP_RIGHT:
                legend_x = (
                    axes_x + self.axes.width + border_width_x + self.legend.margin_x
                )
                legend_y = axes_border_y + self.legend.margin_y
            elements.append(self.legend.render(x=legend_x, y=legend_y))

        figure_elements = []

        if style.figure.background_color is not None:
            figure_elements.append(
                Rectangle(
                    x=0,
                    y=0,
                    height=height,
                    width=width,
                    attrs={"fill": style.figure.background_color.as_hex()},
                )
            )

        figure_elements.extend(
            [
                self.axes.render(x=axes_x, y=axes_y),
                *elements,
            ]
        )
        figure_svg = SVG(
            id="figure",
            height=height,
            width=width,
            children=figure_elements,
        )
        return figure_svg.render(text_as_path=text_as_path)
