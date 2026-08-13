from dataclasses import dataclass, field

from starplot.styles import (
    AlignmentEnum,
    LegendLocationEnum,
)
from starplot.svg.elements import SVG, Defs, Element, Group, Rectangle, create_gradient


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

    def render(self, x: float, y: float) -> Group | SVG | None:
        if self.is_empty:
            return None

        x, y = round(x, 2), round(y, 2)
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
        x, y = round(x, 2), round(y, 2)
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

        x, y = round(x, 2), round(y, 2)
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
    axes_frame: Region = field(default_factory=Region)
    title: Region = field(default_factory=Region)
    legend: LegendRegion = field(default_factory=LegendRegion)
    table: TableRegion = field(default_factory=TableRegion)

    def render(self, style, text_as_path: bool, scale: float):
        """
        Renders each region

        This function is responsible for determining the transform() for each region
        """
        outer_height = max(
            self.axes.height, self.axes_border.height, self.axes_frame.height
        )
        outer_width = max(
            self.axes.width, self.axes_border.width, self.axes_frame.width
        )
        height = (
            style.figure.padding * 2
            + self.title.height
            + outer_height
            + self.table.height
        )
        width = style.figure.padding * 2 + outer_width

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

        # axes, axes_border, and axes_frame all draw their elements using the
        # same underlying coordinate space (Canvas._to_display()'s [0, width] x
        # [0, height], which is what clip_path_display and axes' own markers
        # /polygons/etc are built from). axes_border/axes_frame's geometry is
        # just that same space buffered outward, so it already extends past
        # axes' own [0, width] box on its own -- all three render at the exact
        # same (axes_x, axes_y) translate; nothing here should ever be shifted
        # relative to the others.
        #
        # That outward extent goes negative in local coordinates (e.g. a ring
        # buffered 40px out starts at local x=-40), so axes_x/axes_y need to
        # be pushed forward by that amount -- otherwise the ring's outer edge
        # renders at a negative absolute position and gets clipped by the
        # figure's own bounds instead of leaving `padding` before it.
        outer_buffer_x = (outer_width - self.axes.width) / 2
        outer_buffer_y = (outer_height - self.axes.height) / 2
        outer_x = axes_x
        outer_y = axes_y
        axes_x += outer_buffer_x
        axes_y += outer_buffer_y

        elements = []
        if not self.title.is_empty:
            elements.append(
                self.title.render(x=style.figure.padding, y=style.figure.padding)
            )

        if not self.axes_border.is_empty:
            elements.append(self.axes_border.render(x=axes_x, y=axes_y))

        if not self.axes_frame.is_empty:
            elements.append(self.axes_frame.render(x=axes_x, y=axes_y))

        if not self.table.is_empty:
            table_y = outer_y + outer_height
            if self.table.alignment == AlignmentEnum.RIGHT:
                table_x = outer_x + outer_width - self.table.width
            elif self.table.alignment == AlignmentEnum.CENTER:
                table_x = outer_x + (outer_width - self.table.width) / 2
            else:
                table_x = outer_x
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
                legend_x = outer_x - self.legend.width - self.legend.margin_x
                legend_y = outer_y + self.legend.margin_y
            elif loc == LegendLocationEnum.OUTSIDE_BOTTOM_LEFT:
                legend_x = outer_x - self.legend.width - self.legend.margin_x
                legend_y = (
                    outer_y
                    + self.axes.height
                    - self.legend.height
                    - self.legend.margin_y
                )
            elif loc == LegendLocationEnum.OUTSIDE_BOTTOM_RIGHT:
                legend_x = outer_x + outer_width + self.legend.margin_x
                legend_y = (
                    axes_y
                    + self.axes.height
                    - self.legend.height
                    - self.legend.margin_y
                )
            elif loc == LegendLocationEnum.OUTSIDE_TOP_RIGHT:
                legend_x = outer_x + outer_width + self.legend.margin_x
                legend_y = outer_y + self.legend.margin_y
            elements.append(self.legend.render(x=legend_x, y=legend_y))

        figure_elements = []

        if style.figure.background is not None:
            figure_attrs = style.figure.background.css(scale)

            if isinstance(style.figure.background.fill_color, list):
                gradient = create_gradient(
                    stops=style.figure.background.fill_color,
                    type=style.figure.background.gradient_type,
                    id="figure-background-gradient",
                )
                figure_attrs["fill"] = gradient.url
                figure_elements.append(Defs(children=[gradient]))

            figure_elements.append(
                Rectangle(
                    x=0,
                    y=0,
                    height=height,
                    width=width,
                    attrs=figure_attrs,
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
