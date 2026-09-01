import logging
import math

import numpy as np
import pytest
from shapely import Polygon as ShapelyPolygon
from shapely import box

from starplot import geometry as _geometry
from starplot.projections import (
    CoordinateReferenceSystem,
    Equidistant,
    Orthographic,
    PlateCarree,
)
from starplot.styles import (
    GradientStyle,
    LegendStyle,
    LineStyle,
    MarkerStyle,
    PlotStyle,
    PolygonStyle,
    TableStyle,
    TitleStyle,
)
from starplot.svg import fonts
from starplot.svg.canvas import Canvas, CoordinateSystem
from starplot.svg.elements import Group, Line, Polygon, Polyline, Rectangle
from starplot.utils import normalize

LOGGER = logging.getLogger("starplot-test")


def _canvas(projection, bounds, **kwargs):
    return Canvas(
        resolution=1000,
        projection=projection,
        bounds=list(bounds),
        style=PlotStyle(),
        crs=CoordinateReferenceSystem.WNU,
        logger=LOGGER,
        **kwargs,
    )


class TestCoordinateConversions:
    def test_to_axes_matches_manual_normalize(self):
        # GIVEN a canvas and a data-space (RA/DEC) point
        canvas = _canvas(PlateCarree(), bounds=[10, -40, 80, 40])
        ra, dec = 45, 10
        px, py = canvas.tx.transform(ra, dec)
        expected = (
            normalize(px, canvas.minx, canvas.maxx),
            normalize(py, canvas.miny, canvas.maxy),
        )

        # WHEN converting the point to axes coordinates
        result = canvas._to_axes(ra, dec)

        # THEN it matches normalizing the projected point by hand
        assert result == pytest.approx(expected)

        # AND it's between 0 and 1
        assert 0 <= result[0] <= 1
        assert 0 <= result[1] <= 1

    def test_to_axes_bounds_corners_map_to_unit_square(self):
        # GIVEN a canvas and its own data-space bounds
        canvas = _canvas(PlateCarree(), bounds=[10, -40, 80, 40])

        # WHEN converting the two opposite bounds corners to axes coordinates
        ax0, ay0 = canvas._to_axes(canvas.bounds[0], canvas.bounds[1])
        ax1, ay1 = canvas._to_axes(canvas.bounds[2], canvas.bounds[3])

        # THEN they land on the axes unit square (order may flip under WNU's
        # west-positive longitude axis, so compare the unordered pair)
        assert sorted([ax0, ax1]) == pytest.approx([0, 1], abs=1e-6)
        assert sorted([ay0, ay1]) == pytest.approx([0, 1], abs=1e-6)

    def test_to_display_data_coordinate_system(self):
        # GIVEN a canvas and a data-space (RA/DEC) point
        canvas = _canvas(PlateCarree(), bounds=[10, -40, 80, 40])
        ra, dec = 45, 10
        ax, ay = canvas._to_axes(ra, dec)
        expected_x = round(ax * canvas.width, canvas.precision)
        expected_y = round((1 - ay) * canvas.height, canvas.precision)

        # WHEN converting the point to display coordinates
        dx, dy = canvas._to_display(ra, dec)

        # THEN it matches axes coordinates scaled to the canvas's pixel size
        assert dx == pytest.approx(expected_x)
        assert dy == pytest.approx(expected_y)

    def test_to_display_axes_coordinate_system(self):
        # GIVEN a canvas and a point already in axes (0..1) space
        canvas = _canvas(PlateCarree(), bounds=[10, -40, 80, 40])

        # WHEN converting it to display coordinates as an AXES-space point
        dx, dy = canvas._to_display(0.25, 0.75, cs=CoordinateSystem.AXES)

        # THEN it's scaled directly to pixels, with y flipped
        assert dx == pytest.approx(round(0.25 * canvas.width, canvas.precision))
        assert dy == pytest.approx(round(0.25 * canvas.height, canvas.precision))

    def test_to_display_projected_coordinate_system(self):
        # GIVEN a canvas and a point already projected (but not yet normalized)
        canvas = _canvas(PlateCarree(), bounds=[10, -40, 80, 40])
        px, py = canvas.tx.transform(45, 10)
        ax, ay = canvas._to_axes(45, 10)

        # WHEN converting it to display coordinates as a PROJECTED-space point
        dx, dy = canvas._to_display(px, py, cs=CoordinateSystem.PROJECTED)

        # THEN it matches the same point converted through DATA coordinates
        assert dx == pytest.approx(round(ax * canvas.width, canvas.precision))
        assert dy == pytest.approx(round((1 - ay) * canvas.height, canvas.precision))

    def test_to_display_display_coordinate_system_is_passthrough(self):
        # GIVEN a canvas and an arbitrary point
        canvas = _canvas(PlateCarree(), bounds=[10, -40, 80, 40])

        # WHEN converting it to display coordinates as a DISPLAY-space point
        result = canvas._to_display(123.4, 567.8, cs=CoordinateSystem.DISPLAY)

        # THEN it's returned unchanged
        assert result == (123.4, 567.8)

    def test_to_display_unrecognized_coordinate_system_raises(self):
        # GIVEN a canvas
        canvas = _canvas(PlateCarree(), bounds=[10, -40, 80, 40])

        # WHEN converting a point with an unrecognized coordinate system
        # THEN a ValueError is raised
        with pytest.raises(ValueError, match="Unrecognized coordinate system"):
            canvas._to_display(0, 0, cs="bogus")

    def test_to_display_invert_x_and_y(self):
        # GIVEN a canvas with invert_x/invert_y enabled and an off-center point
        # (off-center so inversion actually changes the result)
        canvas = _canvas(
            PlateCarree(), bounds=[10, -40, 80, 40], invert_x=True, invert_y=True
        )
        ra, dec = 30, -20
        ax, ay = canvas._to_axes(ra, dec)
        expected_x = round(canvas.width - ax * canvas.width, canvas.precision)
        expected_y = round(canvas.height - (1 - ay) * canvas.height, canvas.precision)

        # WHEN converting the point to display coordinates
        dx, dy = canvas._to_display(ra, dec)

        # THEN both axes are mirrored around the canvas's own width/height
        assert dx == pytest.approx(expected_x)
        assert dy == pytest.approx(expected_y)

    def test_to_display_precision_zero_truncates_to_int(self):
        # GIVEN a canvas with precision=0 and an array-valued point
        canvas = _canvas(PlateCarree(), bounds=[10, -40, 80, 40], precision=0)
        xs = np.array([45.2])
        ys = np.array([10.2])

        # WHEN converting the point to display coordinates
        dx, dy = canvas._to_display(xs, ys)

        # THEN the result is truncated to an integer dtype instead of rounded
        assert dx.dtype.kind == "i"
        assert dy.dtype.kind == "i"
        assert dx == 434
        assert dy == 372

    def test_to_display_precision_zero_applies_invert(self):
        # GIVEN a canvas with precision=0 and invert_x/invert_y enabled
        xs = np.array([30.0])
        ys = np.array([-20.0])
        inverted = _canvas(
            PlateCarree(),
            bounds=[10, -40, 80, 40],
            precision=0,
            invert_x=True,
            invert_y=True,
        )
        ax, ay = inverted._to_axes(xs[0], ys[0])
        expected_x = int(inverted.width - ax * inverted.width)
        expected_y = int(inverted.height - (1 - ay) * inverted.height)

        # WHEN converting the point to display coordinates
        dx_inv, dy_inv = inverted._to_display(xs, ys)

        # THEN inversion still applies, even though the result is truncated to int
        assert dx_inv[0] == expected_x
        assert dy_inv[0] == expected_y


class TestSplittingGeometries:
    def test_split_line_with_refinement_no_jump_returns_single_segment(self):
        # GIVEN a canvas and a line with no projection discontinuity
        canvas = _canvas(PlateCarree(), bounds=[0, -90, 360, 90])
        coords = [(170, 0), (171, 0), (172, 0), (173, 0)]
        arr = np.array(coords)
        px, py = canvas.tx.transform(arr[:, 0], arr[:, 1])

        # WHEN splitting the line with refinement
        segments = canvas._split_line_with_refinement(coords, px, py)

        # THEN it comes back as a single, unsplit segment
        assert len(segments) == 1
        assert segments[0] == pytest.approx(list(zip(px, py)))

    def test_split_line_with_refinement_splits_sparse_seam_crossing_line(self):
        # GIVEN a canvas and a sparse (2-point) line crossing the antimeridian seam
        canvas = _canvas(PlateCarree(), bounds=[0, -90, 360, 90])
        coords = [(359, 10), (1, 10)]
        arr = np.array(coords)
        px, py = canvas.tx.transform(arr[:, 0], arr[:, 1])

        # WHEN splitting the line with refinement
        segments = canvas._split_line_with_refinement(coords, px, py)
        span = canvas.maxx - canvas.minx

        # THEN it's split into two segments, each reaching almost all the way to
        # the seam instead of stopping short, with the original endpoints preserved
        assert len(segments) == 2
        assert segments[0][-1][0] == pytest.approx(canvas.minx, abs=1e-3 * span)
        assert segments[1][0][0] == pytest.approx(canvas.maxx, abs=1e-3 * span)
        assert segments[0][0] == pytest.approx((px[0], py[0]))
        assert segments[1][-1] == pytest.approx((px[1], py[1]))

    def test_refine_jump_returns_segments_reaching_the_seam(self):
        # GIVEN a canvas and two RA/DEC points straddling the seam
        canvas = _canvas(PlateCarree(), bounds=[0, -90, 360, 90])
        span = canvas.maxx - canvas.minx

        # WHEN refining the jump between them
        refined = canvas._refine_jump((359, 10), (1, 10))

        # THEN it returns two segments, each reaching almost to the seam
        assert len(refined) == 2
        assert refined[0][-1][0] == pytest.approx(canvas.minx, abs=1e-3 * span)
        assert refined[1][0][0] == pytest.approx(canvas.maxx, abs=1e-3 * span)

    def test_refine_jump_interpolates_shorter_way_around(self):
        # GIVEN a canvas and two RA/DEC points ~2 degrees apart across the seam
        canvas = _canvas(PlateCarree(), bounds=[0, -90, 360, 90])

        # WHEN refining the jump between them
        refined = canvas._refine_jump((359, 10), (1, 10))
        all_x = [x for segment in refined for x, _ in segment]

        # THEN the interpolation stays clustered near the two edges instead of
        # sweeping the long way around through RA 180 (which would pass through
        # the canvas's own center, x near 0)
        assert min(abs(x) for x in all_x) > 0.9 * canvas.maxx


class TestWrappingGeometry:
    def test_clip_wrapped_polygon_no_wrap_returns_original_shape(self):
        # GIVEN a canvas and a small polygon entirely within its bounds
        canvas = _canvas(PlateCarree(), bounds=[10, -40, 80, 40])
        coords = [(30, -5), (40, -5), (40, 5), (30, 5), (30, -5)]
        arr = np.array(coords)
        px, py = canvas.tx.transform(arr[:, 0], arr[:, 1])

        # WHEN clipping the (already-projected) polygon ring
        result = canvas._clip_wrapped_polygon(coords, np.array(px), np.array(py))

        # THEN it comes back unchanged, as a single polygon
        assert len(result) == 1
        assert result[0].equals(ShapelyPolygon(zip(px, py)))

    def test_clip_wrapped_polygon_straddling_seam_stays_small_and_visible(self):
        # GIVEN a canvas and a small circle straddling RA 0/360, like a DSO polygon near the seam
        canvas = _canvas(PlateCarree(), bounds=[0, -90, 360, 90])
        circle_poly = _geometry.circle(center=(0, 0), diameter_degrees=6, num_pts=60)
        coords = list(circle_poly.exterior.coords)
        arr = np.array(coords)
        px, py = canvas.tx.transform(arr[:, 0], arr[:, 1])

        # WHEN clipping the (already-projected) polygon ring
        result = canvas._clip_wrapped_polygon(coords, np.array(px), np.array(py))

        # THEN it stays a compact shape near the two visible edges, not the
        # complement of the shape (which would mean the wrong region got filled)
        assert len(result) == 2
        view = box(canvas.minx, canvas.miny, canvas.maxx, canvas.maxy)
        total_area = sum(p.area for p in result)
        assert total_area / view.area < 0.01
        view_with_margin = view.buffer(1)
        for p in result:
            assert view_with_margin.contains(p)

    def test_clip_wrapped_polygon_with_pole_singularity(self):
        # GIVEN a canvas and a small polygon near the pole, with one vertex's
        # projection forced non-finite (simulating a genuine pole singularity)
        canvas = _canvas(PlateCarree(), bounds=[0, -90, 360, 90])
        coords = [(160, 80), (200, 80), (180, 89.999), (160, 80)]
        arr = np.array(coords)
        px, py = canvas.tx.transform(arr[:, 0], arr[:, 1])
        px = np.array(px, dtype=float)
        py = np.array(py, dtype=float)
        px[2] = np.nan
        py[2] = np.nan

        # WHEN clipping the (already-projected) polygon ring
        result = canvas._clip_wrapped_polygon(coords, px, py)

        # THEN the non-finite point is repaired away, leaving a small cap near
        # the pole rather than everywhere but the cap
        assert len(result) >= 1
        view = box(canvas.minx, canvas.miny, canvas.maxx, canvas.maxy)
        total_area = sum(p.area for p in result)
        assert total_area / view.area < 0.05
        view_with_margin = view.buffer(1)
        for p in result:
            assert view_with_margin.contains(p)


class TestLine:
    def _polylines(self, canvas):
        return [e for _, e in canvas.layout.axes.elements if isinstance(e, Polyline)]

    def test_line_on_non_wrapping_projection_stays_one_segment(self):
        # GIVEN a canvas using a non-wrapping projection and a simple line
        canvas = _canvas(Equidistant(), bounds=[10, -40, 80, 40])
        coords = [(30, -5), (40, -5), (50, 5)]

        # WHEN plotting the line
        canvas.line(coordinates=coords, style=LineStyle())

        # THEN it renders as a single polyline, with points matching the
        # projected/display coordinates exactly (no jump-splitting applies)
        polylines = self._polylines(canvas)
        assert len(polylines) == 1
        arr = np.array(coords)
        px, py = canvas.tx.transform(arr[:, 0], arr[:, 1])
        dx, dy = canvas._to_display(px, py, cs=CoordinateSystem.PROJECTED)
        assert polylines[0].points == pytest.approx(list(zip(dx, dy)))

    def test_line_on_wrapping_projection_splits_at_seam(self):
        # GIVEN a canvas using a wrapping projection and a line crossing RA 0/360
        canvas = _canvas(PlateCarree(), bounds=[0, -90, 360, 90])
        coords = [(355, 0), (357, 0), (359, 0), (1, 0), (3, 0), (5, 0)]

        # WHEN plotting the line
        canvas.line(coordinates=coords, style=LineStyle())

        # THEN it's split into two polylines, one on each side of the seam
        assert len(self._polylines(canvas)) == 2

    def test_line_drops_points_beyond_the_horizon(self):
        # GIVEN a canvas using a hemisphere-limited projection (Orthographic)
        # and a line where the last point is beyond its 90-degree horizon
        canvas = _canvas(Orthographic(), bounds=[0, -90, 360, 90])
        coords = [(180, 0), (200, 0), (220, 0), (240, 0), (260, 0), (280, 0)]

        # WHEN plotting the line
        canvas.line(coordinates=coords, style=LineStyle())

        # THEN the resulting polyline only includes the points within the
        # horizon, dropping the last (100 degrees from center) point
        polylines = self._polylines(canvas)
        assert len(polylines) == 1
        assert len(polylines[0].points) == len(coords) - 1

    def test_line_entirely_beyond_horizon_renders_nothing(self):
        # GIVEN a canvas using Orthographic and a line entirely beyond its horizon
        canvas = _canvas(Orthographic(), bounds=[0, -90, 360, 90])
        coords = [(0, 0), (5, 0), (10, 0)]

        # WHEN plotting the line
        canvas.line(coordinates=coords, style=LineStyle())

        # THEN nothing is rendered
        assert self._polylines(canvas) == []


class TestPolygon:
    def _polygons(self, canvas):
        return [
            e
            for _, e in canvas.layout.axes.elements
            if isinstance(e, Polygon) and e is not canvas.background_element
        ]

    def test_polygon_projected_cs_bypasses_wrap_clipping(self):
        # GIVEN a canvas using a wrapping projection, and a ring that DOES get
        # split into two pieces when clipped as DATA (RA/DEC) coordinates
        # straddling the seam (see TestWrappingGeometry)
        circle_poly = _geometry.circle(center=(0, 0), diameter_degrees=6, num_pts=60)
        coords = list(circle_poly.exterior.coords)

        canvas_data = _canvas(PlateCarree(), bounds=[0, -90, 360, 90])
        canvas_data.polygon(coords, PolygonStyle(), cs=CoordinateSystem.DATA)

        canvas_projected = _canvas(PlateCarree(), bounds=[0, -90, 360, 90])

        # WHEN plotting the same ring as already-PROJECTED coordinates instead
        canvas_projected.polygon(coords, PolygonStyle(), cs=CoordinateSystem.PROJECTED)

        # THEN the DATA version is split into two pieces, but the PROJECTED
        # version bypasses wrap clipping entirely and stays a single polygon
        # with every vertex from the input ring intact
        assert len(self._polygons(canvas_data)) == 2
        projected_polys = self._polygons(canvas_projected)
        assert len(projected_polys) == 1
        assert len(projected_polys[0].points) == len(coords)

    def test_polygon_entirely_beyond_horizon_renders_nothing(self):
        # GIVEN a canvas using Orthographic and a ring on the far side of the
        # globe from the projection's center (180 degrees away, fully invisible)
        canvas = _canvas(Orthographic(), bounds=[0, -90, 360, 90])
        coords = list(
            _geometry.circle(
                center=(0, 0), diameter_degrees=10, num_pts=30
            ).exterior.coords
        )

        # WHEN plotting the ring
        canvas.polygon(coords, PolygonStyle())

        # THEN nothing is rendered
        assert self._polygons(canvas) == []

    def test_polygon_fully_within_horizon_stays_whole(self):
        # GIVEN a canvas using Orthographic and a ring centered on the
        # projection's own center (fully within its 90-degree horizon)
        canvas = _canvas(Orthographic(), bounds=[0, -90, 360, 90])
        coords = list(
            _geometry.circle(
                center=(180, 0), diameter_degrees=10, num_pts=30
            ).exterior.coords
        )

        # WHEN plotting the ring
        canvas.polygon(coords, PolygonStyle())

        # THEN it renders as a single, unsplit polygon
        assert len(self._polygons(canvas)) == 1


class TestLegend:
    def _text_hw(self, text, style):
        h, w, _ = fonts.get_text_hw(
            text=text,
            font_name=style.font_name,
            font_size=style.font_size,
            font_weight=style.font_weight,
            italic=style.font_style == "italic",
        )
        return h, w

    def test_legend_single_label_no_title(self):
        # GIVEN a canvas and a legend style, sized in real font metrics
        canvas = _canvas(PlateCarree(), bounds=[10, -40, 80, 40])
        style = LegendStyle()
        label_h, label_w = self._text_hw("Star", style.labels)

        # WHEN plotting a legend with a single section, no title, one label
        canvas.legend(sections=[("", {"Star": (MarkerStyle(), None)})], style=style)

        # THEN height/width match the padding + one label row + marker/text,
        # derived independently from the style's own padding constants
        expected_height = (
            style.padding_y * 2
            + max(style.symbol_size, label_h)
            + 2 * style.label_padding
        )
        expected_width = (
            label_w + style.symbol_size + style.symbol_padding + style.padding_x * 2
        )
        assert canvas.layout.legend.height == pytest.approx(expected_height)
        assert canvas.layout.legend.width == pytest.approx(expected_width)

    def test_legend_title_adds_two_line_heights_and_extra_padding(self):
        # GIVEN a canvas and a legend style
        canvas = _canvas(PlateCarree(), bounds=[10, -40, 80, 40])
        style = LegendStyle()
        title_h, title_w = self._text_hw("My Title", style.title)
        label_h, _ = self._text_hw("Star", style.labels)

        # WHEN plotting a legend with a titled section and one label
        canvas.legend(
            sections=[("My Title", {"Star": (MarkerStyle(), None)})], style=style
        )

        # THEN the title contributes twice its own height plus its own
        # padding line, on top of the single-label case
        expected_height = (
            style.padding_y * 2
            + 2 * title_h
            + max(style.symbol_size, label_h)
            + 3 * style.label_padding
        )
        assert canvas.layout.legend.height == pytest.approx(expected_height)
        # the title can also widen the legend beyond what the label needs
        assert canvas.layout.legend.width >= title_w

    def test_legend_height_grows_with_each_additional_label(self):
        # GIVEN two canvases and a legend style
        canvas_one = _canvas(PlateCarree(), bounds=[10, -40, 80, 40])
        canvas_two = _canvas(PlateCarree(), bounds=[10, -40, 80, 40])
        style = LegendStyle()

        # WHEN plotting legends with one vs two labels in the same section
        canvas_one.legend(sections=[("", {"Star": (MarkerStyle(), None)})], style=style)
        canvas_two.legend(
            sections=[
                (
                    "",
                    {
                        "Star": (MarkerStyle(), None),
                        "Bright Star": (MarkerStyle(), None),
                    },
                )
            ],
            style=style,
        )

        # THEN each extra label adds its own row -- height grows accordingly
        bright_h, _ = self._text_hw("Bright Star", style.labels)
        expected_extra = max(style.symbol_size, bright_h) + style.label_padding
        assert canvas_two.layout.legend.height == pytest.approx(
            canvas_one.layout.legend.height + expected_extra
        )

    def test_legend_height_grows_with_each_additional_section(self):
        # GIVEN two canvases and a legend style
        canvas_one = _canvas(PlateCarree(), bounds=[10, -40, 80, 40])
        canvas_two = _canvas(PlateCarree(), bounds=[10, -40, 80, 40])
        style = LegendStyle()

        # WHEN plotting legends with one vs two untitled sections
        canvas_one.legend(sections=[("", {"Star": (MarkerStyle(), None)})], style=style)
        canvas_two.legend(
            sections=[
                ("", {"Star": (MarkerStyle(), None)}),
                ("", {"Star": (MarkerStyle(), None)}),
            ],
            style=style,
        )

        # THEN a second section adds its own full row plus an extra
        # inter-section padding gap (unlike a same-section extra label)
        label_h, _ = self._text_hw("Star", style.labels)
        expected_extra = max(style.symbol_size, label_h) + 2 * style.label_padding
        assert canvas_two.layout.legend.height == pytest.approx(
            canvas_one.layout.legend.height + expected_extra
        )


class TestTable:
    def _cell_width(self, value, style, scale=1.0):
        _, w, _ = fonts.get_text_hw(
            text=str(value),
            font_name=style.font_name,
            font_size=style.font_size * scale,
            font_weight=style.font_weight,
            italic=style.font_style == "italic",
        )
        return w

    def test_table_dimensions_match_column_and_row_metrics(self):
        # GIVEN a canvas, a table style, and a small table of data
        canvas = _canvas(PlateCarree(), bounds=[10, -40, 80, 40])
        style = TableStyle()
        headers = ["Name", "Magnitude"]
        rows = [["Vega", "0.03"], ["Sirius", "-1.46"]]

        # WHEN plotting the table
        canvas.table(headers=headers, rows=rows, style=style)

        # THEN each column's width is the widest cell (header or data) in
        # that column, plus padding on both sides, and the table's overall
        # height covers the header row plus every data row
        padding_x, padding_y = 28, 20  # canvas.table()'s own defaults
        col_widths = [
            max(
                self._cell_width(headers[c], style.header),
                *[self._cell_width(row[c], style.cell) for row in rows],
            )
            + padding_x * 2
            for c in range(len(headers))
        ]
        header_height = style.header.font_size + padding_y * 2
        row_height = style.cell.font_size + padding_y * 2
        expected_width = sum(col_widths)
        expected_height = style.padding_top + header_height + row_height * len(rows)

        assert canvas.layout.table.width == pytest.approx(expected_width)
        assert canvas.layout.table.height == pytest.approx(expected_height)

    def test_table_border_lines_separate_columns_rows_and_header(self):
        # GIVEN a canvas, a table style, and a table with 2 columns and 3 rows
        canvas = _canvas(PlateCarree(), bounds=[10, -40, 80, 40])
        style = TableStyle()
        headers = ["Name", "Magnitude"]
        rows = [["Vega", "0.03"], ["Sirius", "-1.46"], ["Rigel", "0.13"]]

        # WHEN plotting the table
        canvas.table(headers=headers, rows=rows, style=style)

        lines = [e for _, e in canvas.layout.table.elements if isinstance(e, Line)]
        rects = [e for _, e in canvas.layout.table.elements if isinstance(e, Rectangle)]

        # THEN there's one vertical separator per internal column boundary
        # (num_cols - 1), one horizontal line under the header, and one more
        # per internal row boundary (len(rows) - 1) -- but none below the
        # very last row, since the border rectangle already closes it off
        assert len(lines) == (len(headers) - 1) + 1 + (len(rows) - 1)
        vertical = [line for line in lines if line.x1 == line.x2]
        horizontal = [line for line in lines if line.y1 == line.y2]
        assert len(vertical) == len(headers) - 1
        assert len(horizontal) == 1 + (len(rows) - 1)

        # AND a single border rectangle wraps the whole table exactly
        assert len(rects) == 1
        border = rects[0]
        assert border.x == 0
        assert border.width == pytest.approx(canvas.layout.table.width)
        assert border.y + border.height == pytest.approx(canvas.layout.table.height)


class TestInitBounds:
    def test_clip_path_constrains_bounds_to_its_own_extent(self):
        # GIVEN the same projection/bounds, once with a clip_path covering
        # only part of them, and once without any clip_path
        clip_path = ShapelyPolygon(
            [(20, -10), (60, -10), (60, 20), (20, 20), (20, -10)]
        )

        # WHEN constructing each canvas
        clipped = _canvas(PlateCarree(), bounds=[10, -40, 80, 40], clip_path=clip_path)
        unclipped = _canvas(PlateCarree(), bounds=[10, -40, 80, 40])

        # THEN the clipped canvas's projected bounds are snapped to the clip
        # path's own (smaller) extent, not the originally requested bounds
        assert (clipped.maxx - clipped.minx) < (unclipped.maxx - unclipped.minx)
        assert clipped.bounds == pytest.approx((20, -10, 60, 20), abs=1e-6)

    def test_global_bounds_use_projections_own_global_bounds(self):
        # GIVEN a canvas whose requested bounds span the whole sky
        canvas = _canvas(PlateCarree(), bounds=[0, -90, 360, 90])

        # WHEN it initializes its bounds
        # THEN it's recognized as global, and takes its projected extent
        # directly from the projection (not by densifying the user's bounds)
        assert canvas._is_global()
        assert canvas.projected_bounds == canvas.projection.global_bounds
        assert canvas.bounds == pytest.approx((1e-7, -90, 359.999999, 90))

    def test_ra_0_360_epsilon_nudge_avoids_degenerate_bounds(self):
        # GIVEN a (non-global) canvas whose bounds touch RA 0 and 360 exactly
        # -- a projection singularity for a plain cylindrical projection --
        # but with a small enough dec span to not trigger the global-bounds
        # branch above
        canvas = _canvas(PlateCarree(), bounds=[0, -40, 360, 40])

        # WHEN it initializes its bounds
        # THEN it's still non-global, and the projected width stays
        # non-degenerate (a zero-width span here would later divide by zero
        # in _refresh_figure_dimensions's aspect-ratio math)
        assert not canvas._is_global()
        assert canvas.minx != canvas.maxx
        assert math.isfinite(canvas.minx) and math.isfinite(canvas.maxx)


class TestRefreshFigureDimensions:
    def test_wide_bounds_fill_width_and_derive_height_from_aspect_ratio(self):
        # GIVEN bounds much wider (in RA) than tall (in DEC)
        canvas = _canvas(PlateCarree(), bounds=[10, -20, 100, 10])
        span_x = abs(canvas.maxx - canvas.minx)
        span_y = abs(canvas.maxy - canvas.miny)
        assert span_x > span_y  # sanity check on the fixture itself

        # WHEN the canvas computes its figure dimensions
        # THEN width is set to the full resolution, and height is derived to
        # preserve the projected aspect ratio
        assert canvas.width == canvas.resolution
        assert canvas.height / canvas.width == pytest.approx(span_y / span_x)

    def test_tall_bounds_fill_height_and_derive_width_from_aspect_ratio(self):
        # GIVEN bounds much taller (in DEC) than wide (in RA)
        canvas = _canvas(PlateCarree(), bounds=[10, -60, 30, 60])
        span_x = abs(canvas.maxx - canvas.minx)
        span_y = abs(canvas.maxy - canvas.miny)
        assert span_y > span_x  # sanity check on the fixture itself

        # WHEN the canvas computes its figure dimensions
        # THEN height is set to the full resolution, and width is derived to
        # preserve the projected aspect ratio
        assert canvas.height == canvas.resolution
        assert canvas.width / canvas.height == pytest.approx(span_x / span_y)


class TestGroup:
    def test_group_wraps_its_elements_in_a_single_group(self):
        # GIVEN a canvas
        canvas = _canvas(PlateCarree(), bounds=[10, -40, 80, 40])
        before = len(canvas.layout.axes.elements)

        # WHEN drawing two markers inside a group() context
        with canvas.group(gid="g1"):
            canvas.marker(30, 0, MarkerStyle())
            canvas.marker(40, 0, MarkerStyle())

        # THEN exactly one new element is added -- a single Group containing
        # both markers, not two separate top-level elements
        added = canvas.layout.axes.elements[before:]
        assert len(added) == 1
        _, group = added[0]
        assert isinstance(group, Group)
        assert group.id == "g1"
        assert len(group.children) == 2

    def test_group_zorder_defaults_to_its_lowest_child_zorder(self):
        # GIVEN a canvas
        canvas = _canvas(PlateCarree(), bounds=[10, -40, 80, 40])

        # WHEN drawing markers with different zorders inside a group with no
        # explicit zorder of its own
        with canvas.group():
            canvas.marker(30, 0, MarkerStyle(zorder=5))
            canvas.marker(40, 0, MarkerStyle(zorder=2))

        # THEN the group's own zorder is the minimum of its children's
        group_zorder, _ = canvas.layout.axes.elements[-1]
        assert group_zorder == 2

    def test_group_explicit_zorder_overrides_the_default(self):
        # GIVEN a canvas
        canvas = _canvas(PlateCarree(), bounds=[10, -40, 80, 40])

        # WHEN drawing a marker inside a group with an explicit zorder
        with canvas.group(zorder=99):
            canvas.marker(30, 0, MarkerStyle(zorder=5))

        # THEN the group uses that explicit zorder instead of its child's
        group_zorder, _ = canvas.layout.axes.elements[-1]
        assert group_zorder == 99

    def test_nested_groups_combine_into_a_single_outer_group(self):
        # GIVEN a canvas
        canvas = _canvas(PlateCarree(), bounds=[10, -40, 80, 40])

        # WHEN drawing a marker, then nesting another group with its own
        # marker inside the same outer group
        with canvas.group(gid="outer"):
            canvas.marker(30, 0, MarkerStyle())
            with canvas.group(gid="inner"):
                canvas.marker(40, 0, MarkerStyle())

        # THEN the outer group has exactly 2 children -- its own marker, and
        # the inner group as a single nested element (not flattened together)
        _, outer = canvas.layout.axes.elements[-1]
        assert len(outer.children) == 2
        assert isinstance(outer.children[1], Group)
        assert outer.children[1].id == "inner"

    def test_empty_group_adds_nothing(self):
        # GIVEN a canvas
        canvas = _canvas(PlateCarree(), bounds=[10, -40, 80, 40])
        before = len(canvas.layout.axes.elements)

        # WHEN entering a group context without drawing anything inside it
        with canvas.group(gid="empty"):
            pass

        # THEN nothing is added
        assert len(canvas.layout.axes.elements) == before


class TestGetOrCreateGradient:
    def test_creates_and_registers_a_new_gradient(self):
        # GIVEN a canvas and a gradient style
        canvas = _canvas(PlateCarree(), bounds=[10, -40, 80, 40])
        before = len(canvas.layout.axes.defs)

        # WHEN resolving it for the first time
        url = canvas._get_or_create_gradient(
            GradientStyle(stops=((0.0, "#7abfff"), (1.0, "#3f7ee3")))
        )

        # THEN a new gradient is registered in the axes defs, and the
        # returned url references it
        assert len(canvas.layout.axes.defs) == before + 1
        assert url.startswith("url(#")

    def test_same_content_with_no_id_reuses_the_cached_gradient(self):
        # GIVEN a canvas and two GradientStyles with identical stops
        canvas = _canvas(PlateCarree(), bounds=[10, -40, 80, 40])
        style_a = GradientStyle(stops=((0.0, "#7abfff"), (1.0, "#3f7ee3")))
        style_b = GradientStyle(stops=((0.0, "#7abfff"), (1.0, "#3f7ee3")))

        # WHEN resolving both, neither with an explicit id
        url_a = canvas._get_or_create_gradient(style_a)
        before = len(canvas.layout.axes.defs)
        url_b = canvas._get_or_create_gradient(style_b)

        # THEN the second resolves to the same (content-hash-based) gradient
        # instead of creating a duplicate
        assert url_b == url_a
        assert len(canvas.layout.axes.defs) == before

    def test_different_content_with_no_id_creates_separate_gradients(self):
        # GIVEN a canvas and two GradientStyles with different stops
        canvas = _canvas(PlateCarree(), bounds=[10, -40, 80, 40])
        before = len(canvas.layout.axes.defs)

        # WHEN resolving both, neither with an explicit id
        url_a = canvas._get_or_create_gradient(
            GradientStyle(stops=((0.0, "#7abfff"), (1.0, "#3f7ee3")))
        )
        url_b = canvas._get_or_create_gradient(
            GradientStyle(stops=((0.0, "#000000"), (1.0, "#ffffff")))
        )

        # THEN they resolve to two distinct gradients
        assert url_a != url_b
        assert len(canvas.layout.axes.defs) == before + 2

    def test_explicit_id_reuses_by_id_even_with_different_content(self):
        # GIVEN a canvas, and two GradientStyles with different stops
        canvas = _canvas(PlateCarree(), bounds=[10, -40, 80, 40])
        before = len(canvas.layout.axes.defs)
        first = GradientStyle(stops=((0.0, "#111111"), (1.0, "#222222")))
        second = GradientStyle(stops=((0.0, "#999999"), (1.0, "#888888")))

        # WHEN resolving both under the SAME explicit id
        url_first = canvas._get_or_create_gradient(first, id="bg-gradient")
        url_second = canvas._get_or_create_gradient(second, id="bg-gradient")

        # THEN the second call reuses whatever was registered under that id
        # first, ignoring its own (different) content entirely
        assert url_second == url_first
        assert len(canvas.layout.axes.defs) == before + 1
        stored = canvas.layout.axes.defs["bg-gradient"]
        assert (
            stored.children[-1].attrs["stop-color"] == "rgb(17,17,17)"
        )  # from `first`


class TestTitle:
    def test_title_region_dimensions_and_text_position(self):
        # GIVEN a canvas and a title style
        canvas = _canvas(PlateCarree(), bounds=[10, -40, 80, 40])
        style = TitleStyle(font_size=42, padding_bottom=20)

        # WHEN plotting a title
        canvas.title("My Title", style)

        # THEN the title region's height/width are derived from the style's
        # own font size/padding and the axes' width
        region = canvas.layout.title
        scale = canvas.scale
        assert region.height == pytest.approx(
            style.font_size * scale + style.padding_bottom * scale
        )
        assert region.width == pytest.approx(canvas.layout.axes.width)

        # AND the text itself is horizontally centered on the axes, anchored
        # by its own font-size/padding math
        _, text = region.elements[0]
        assert text.x == pytest.approx(canvas.layout.axes.width / 2)
        assert text.y == pytest.approx(
            style.font_size * scale - style.padding_bottom * scale
        )
        assert text.attrs["text-anchor"] == "middle"
        assert text.text == "My Title"


class TestExport:
    def test_export_svg_writes_valid_svg_file(self, tmp_path):
        # GIVEN a canvas with something drawn on it
        canvas = _canvas(PlateCarree(), bounds=[10, -40, 80, 40])
        canvas.marker(30, 0, MarkerStyle())
        out_file = tmp_path / "out.svg"

        # WHEN exporting to a svg file
        canvas.export(str(out_file))

        # THEN it writes a valid SVG document that matches render()
        content = out_file.read_text()
        assert content.startswith("<svg")
        assert content.rstrip().endswith("</svg>")
        assert content == canvas.render()
