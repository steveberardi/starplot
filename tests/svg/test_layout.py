import re

import pytest

from starplot.styles import FigureStyle, HorizontalAlignment, LegendLocation, PlotStyle
from starplot.svg.elements import Rectangle
from starplot.svg.layout import Layout, LegendRegion, TableRegion

PADDING = 30
AXES_WIDTH = 1000
AXES_HEIGHT = 800


def _style():
    return PlotStyle(figure=FigureStyle(padding=PADDING))


def _layout(legend=None, table=None):
    layout = Layout()
    layout.axes.width = AXES_WIDTH
    layout.axes.height = AXES_HEIGHT
    layout.axes.elements = [(0, Rectangle(x=0, y=0, height=1, width=1))]
    if legend is not None:
        layout.legend = legend
    if table is not None:
        layout.table = table
    return layout


def _marker_transform(svg: str, marker_id: str) -> tuple[float, float]:
    pattern = (
        r'<g transform="translate\(([\d.\-]+), ([\d.\-]+)\)">\s*<rect id="'
        rf"{re.escape(marker_id)}\""
    )
    match = re.search(pattern, svg)
    assert match, f"marker '{marker_id}' not found in rendered SVG"
    return float(match.group(1)), float(match.group(2))


class TestLegendPositioning:
    LEGEND_WIDTH = 150
    LEGEND_HEIGHT = 100
    MARGIN_X = 10
    MARGIN_Y = 15

    def _render_legend(self, location):
        legend = LegendRegion(
            elements=[(1, Rectangle(id="legend-marker", x=0, y=0, height=1, width=1))],
            height=self.LEGEND_HEIGHT,
            width=self.LEGEND_WIDTH,
            location=location,
            margin_x=self.MARGIN_X,
            margin_y=self.MARGIN_Y,
        )
        layout = _layout(legend=legend)
        svg = layout.render(style=_style(), text_as_path=False, scale=1.0)
        return _marker_transform(svg, "legend-marker")

    @pytest.mark.parametrize(
        "location,expected",
        [
            (
                LegendLocation.INSIDE_TOP_LEFT,
                (PADDING + MARGIN_X, PADDING + MARGIN_Y),
            ),
            (
                LegendLocation.INSIDE_TOP_RIGHT,
                (
                    PADDING + AXES_WIDTH - LEGEND_WIDTH - MARGIN_X,
                    PADDING + MARGIN_Y,
                ),
            ),
            (
                LegendLocation.INSIDE_BOTTOM_LEFT,
                (
                    PADDING + MARGIN_X,
                    PADDING + AXES_HEIGHT - LEGEND_HEIGHT - MARGIN_Y,
                ),
            ),
            (
                LegendLocation.INSIDE_BOTTOM_RIGHT,
                (
                    PADDING + AXES_WIDTH - LEGEND_WIDTH - MARGIN_X,
                    PADDING + AXES_HEIGHT - LEGEND_HEIGHT - MARGIN_Y,
                ),
            ),
            (
                LegendLocation.OUTSIDE_TOP_LEFT,
                (PADDING, PADDING + MARGIN_Y),
            ),
            (
                LegendLocation.OUTSIDE_BOTTOM_LEFT,
                (
                    PADDING,
                    PADDING + AXES_HEIGHT - LEGEND_HEIGHT - MARGIN_Y,
                ),
            ),
            (
                LegendLocation.OUTSIDE_BOTTOM_RIGHT,
                (
                    PADDING + AXES_WIDTH + MARGIN_X,
                    PADDING + AXES_HEIGHT - LEGEND_HEIGHT - MARGIN_Y,
                ),
            ),
            (
                LegendLocation.OUTSIDE_TOP_RIGHT,
                (PADDING + AXES_WIDTH + MARGIN_X, PADDING + MARGIN_Y),
            ),
        ],
    )
    def test_legend_location_positioning(self, location, expected):
        # GIVEN a layout with an axes region and a legend at a given location
        # WHEN rendering the layout
        actual = self._render_legend(location)

        # THEN the legend's translate() matches that location's own corner
        # math (inside corners hug the axes; outside corners sit just beyond
        # it, offset by the legend's own width where it pushes the axes over)
        assert actual == pytest.approx(expected)


class TestTableAlignment:
    TABLE_WIDTH = 300
    TABLE_HEIGHT = 120

    def _render_table(self, alignment):
        table = TableRegion(
            elements=[(1, Rectangle(id="table-marker", x=0, y=0, height=1, width=1))],
            height=self.TABLE_HEIGHT,
            width=self.TABLE_WIDTH,
            alignment=alignment,
        )
        layout = _layout(table=table)
        svg = layout.render(style=_style(), text_as_path=False, scale=1.0)
        return _marker_transform(svg, "table-marker")

    @pytest.mark.parametrize(
        "alignment,expected_x",
        [
            (HorizontalAlignment.LEFT, PADDING),
            (HorizontalAlignment.CENTER, PADDING + (AXES_WIDTH - TABLE_WIDTH) / 2),
            (HorizontalAlignment.RIGHT, PADDING + AXES_WIDTH - TABLE_WIDTH),
        ],
    )
    def test_table_horizontal_alignment(self, alignment, expected_x):
        # GIVEN a layout with an axes region and a table with a given alignment
        # WHEN rendering the layout
        actual_x, actual_y = self._render_table(alignment)

        # THEN the table sits below the axes, and its x position reflects
        # the requested alignment relative to the axes region
        assert actual_x == pytest.approx(expected_x)
        assert actual_y == pytest.approx(PADDING + AXES_HEIGHT)
