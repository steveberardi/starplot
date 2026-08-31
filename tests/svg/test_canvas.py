import logging

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
from starplot.styles import LineStyle, PlotStyle, PolygonStyle
from starplot.svg.canvas import Canvas, CoordinateSystem
from starplot.svg.elements import Polygon, Polyline
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
