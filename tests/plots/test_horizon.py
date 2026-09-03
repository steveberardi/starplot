import pytest
from shapely import MultiPolygon, Polygon

from starplot import HorizonPlot, Observer
from starplot.plots.horizon import generate_ground_polygon
from starplot.svg.elements import Polygon as SvgPolygon
from starplot.svg.elements import Polyline


class TestGenerateGroundPolygon:
    def test_raises_when_azimuth_end_not_greater_than_start(self):
        with pytest.raises(
            ValueError, match="azimuth_end must be greater than azimuth_start"
        ):
            generate_ground_polygon(max_altitude=10, azimuth_start=90, azimuth_end=0)

    def test_raises_when_min_altitude_more_than_max(self):
        with pytest.raises(
            ValueError, match="min_altitude must be less than max_altitude"
        ):
            generate_ground_polygon(
                max_altitude=2, min_altitude=10, azimuth_start=0, azimuth_end=90
            )

    def test_returns_closed_polygon_with_expected_point_count(self):
        coords = generate_ground_polygon(
            max_altitude=10,
            min_altitude=2,
            azimuth_start=0,
            azimuth_end=90,
            num_points=50,
            seed=1,
        )
        # the sampled ground line, plus 2 points that close the shape down
        # to 0 altitude at each end
        assert len(coords) == 52
        assert coords[-2] == (90, 0.0)
        assert coords[-1] == (0, 0.0)

    def test_ground_line_spans_the_full_azimuth_and_altitude_range(self):
        coords = generate_ground_polygon(
            max_altitude=10,
            min_altitude=2,
            azimuth_start=0,
            azimuth_end=90,
            num_points=50,
            seed=1,
        )
        ground_line = coords[:-2]
        azimuths = [c[0] for c in ground_line]
        altitudes = [c[1] for c in ground_line]

        assert min(azimuths) == pytest.approx(0)
        assert max(azimuths) == pytest.approx(90)
        # the noise is normalized to [min_altitude, max_altitude], so both
        # ends of that range should actually be reached
        assert min(altitudes) == pytest.approx(2)
        assert max(altitudes) == pytest.approx(10)

    def test_all_altitudes_stay_within_the_requested_range(self):
        coords = generate_ground_polygon(
            max_altitude=10,
            min_altitude=2,
            azimuth_start=0,
            azimuth_end=360,
            num_points=200,
            seed=7,
        )
        altitudes = [c[1] for c in coords[:-2]]
        assert all(2 <= a <= 10 for a in altitudes)

    def test_same_seed_is_deterministic(self):
        a = generate_ground_polygon(10, 2, 0, 90, 50, seed=42)
        b = generate_ground_polygon(10, 2, 0, 90, 50, seed=42)
        assert a == b

    def test_different_seeds_produce_different_output(self):
        a = generate_ground_polygon(10, 2, 0, 90, 50, seed=1)
        b = generate_ground_polygon(10, 2, 0, 90, 50, seed=2)
        assert a != b


class TestHorizonPlotValidation:
    def test_raises_when_azimuth_min_more_than_max(self):
        with pytest.raises(ValueError, match="Azimuth min must be less than max"):
            HorizonPlot(altitude=(0, 40), azimuth=(120, 90), observer=Observer())

    def test_raises_when_azimuth_range_too_large(self):
        with pytest.raises(
            ValueError, match="Azimuth range cannot be greater than 180"
        ):
            HorizonPlot(altitude=(0, 40), azimuth=(0, 200), observer=Observer())

    def test_raises_when_altitude_min_more_than_max(self):
        with pytest.raises(ValueError, match="Altitude min must be less than max"):
            HorizonPlot(altitude=(40, 0), azimuth=(90, 120), observer=Observer())

    def test_raises_when_altitude_range_too_large(self):
        with pytest.raises(
            ValueError, match="Altitude range cannot be greater than 90"
        ):
            HorizonPlot(altitude=(0, 100), azimuth=(90, 120), observer=Observer())


class TestHorizonPlotCenter:
    def test_center_is_the_midpoint_of_each_range(self):
        p = HorizonPlot(altitude=(0, 40), azimuth=(90, 120), observer=Observer())
        assert p.center_alt == 20
        assert p.center_az == 105

    def test_center_azimuth_wraps_past_360(self):
        # midpoint of (350, 390) is 370, which should wrap back to 10
        p = HorizonPlot(altitude=(0, 40), azimuth=(350, 390), observer=Observer())
        assert p.center_az == 10


class TestHorizonPlotExtentMask:
    def test_returns_a_single_polygon_when_not_crossing_north(self):
        p = HorizonPlot(altitude=(0, 40), azimuth=(90, 120), observer=Observer())
        assert isinstance(p._extent_mask_altaz(), Polygon)

    def test_returns_two_polygons_when_crossing_north(self):
        p = HorizonPlot(altitude=(0, 40), azimuth=(350, 390), observer=Observer())
        mask = p._extent_mask_altaz()

        assert isinstance(mask, MultiPolygon)
        assert len(mask.geoms) == 2
        # one piece hugs the 0 edge, the other hugs the 360 edge, together
        # covering the full azimuth range on either side of North
        bounds = sorted(g.bounds for g in mask.geoms)
        assert bounds[0][0] == pytest.approx(0, abs=1)
        assert bounds[1][2] == pytest.approx(360, abs=1)


class TestHorizonPlotInBounds:
    def test_point_at_center_is_in_bounds(self):
        p = HorizonPlot(altitude=(0, 40), azimuth=(90, 120), observer=Observer())
        assert p.in_bounds_altaz(p.center_alt, p.center_az) is True

    def test_point_far_outside_is_not_in_bounds(self):
        p = HorizonPlot(altitude=(0, 40), azimuth=(90, 120), observer=Observer())
        assert p.in_bounds_altaz(80, 200) is False


class TestHorizonPlotPosition:
    def test_dec_range_is_derived_from_observer_latitude(self):
        p = HorizonPlot(
            altitude=(0, 40),
            azimuth=(90, 120),
            observer=Observer(lat=32.97, lon=-117.038611),
        )
        assert p.dec_min == 32.97 - 90
        assert p.dec_max == 32.97 + 90

    def test_ra_range_covers_the_whole_sky(self):
        p = HorizonPlot(altitude=(0, 40), azimuth=(90, 120), observer=Observer())
        assert p.ra_min == 0
        assert p.ra_max == 360


class TestHorizonPlotPrepareCoords:
    def test_ra_above_360_wraps_to_the_same_result(self):
        p = HorizonPlot(
            altitude=(0, 40),
            azimuth=(90, 120),
            observer=Observer(lat=32.97, lon=-117.038611),
        )
        assert p._prepare_coords(370, 10) == p._prepare_coords(10, 10)

    def test_ra_below_zero_wraps_to_the_same_result(self):
        p = HorizonPlot(
            altitude=(0, 40),
            azimuth=(90, 120),
            observer=Observer(lat=32.97, lon=-117.038611),
        )
        assert p._prepare_coords(-10, 10) == p._prepare_coords(350, 10)

    def test_in_bounds_matches_in_bounds_altaz_of_the_prepared_coords(self):
        p = HorizonPlot(
            altitude=(0, 40),
            azimuth=(90, 120),
            observer=Observer(lat=32.97, lon=-117.038611),
        )
        az, alt = p._prepare_coords(10, 10)
        assert p.in_bounds(10, 10) == p.in_bounds_altaz(alt, az)

    def test_in_bounds_ra_wraparound_is_consistent(self):
        p = HorizonPlot(
            altitude=(0, 40),
            azimuth=(90, 120),
            observer=Observer(lat=32.97, lon=-117.038611),
        )
        assert p.in_bounds(370, 10) == p.in_bounds(10, 10)


class TestHorizonPlotGround:
    def test_adds_a_polygon_to_the_canvas(self):
        p = HorizonPlot(altitude=(0, 40), azimuth=(90, 120), observer=Observer())
        before = [
            e
            for _, e in p.canvas.layout.axes.elements
            if isinstance(e, SvgPolygon) and e is not p.canvas.background_element
        ]
        assert before == []

        p.ground()

        after = [
            e
            for _, e in p.canvas.layout.axes.elements
            if isinstance(e, SvgPolygon) and e is not p.canvas.background_element
        ]
        assert len(after) == 1

    def test_builds_a_ground_rtree_index(self):
        p = HorizonPlot(altitude=(0, 40), azimuth=(90, 120), observer=Observer())
        p.ground()
        assert p._ground_rtree.count(p._ground_rtree.bounds) == 1


class TestHorizonPlotGridlines:
    def test_adds_polylines_to_the_canvas(self):
        p = HorizonPlot(altitude=(0, 40), azimuth=(90, 120), observer=Observer())
        before = [
            e for _, e in p.canvas.layout.axes.elements if isinstance(e, Polyline)
        ]
        assert before == []

        p.gridlines()

        after = [e for _, e in p.canvas.layout.axes.elements if isinstance(e, Polyline)]
        assert len(after) > 0

    def test_default_azimuth_labels_use_cardinal_directions(self):
        # azimuth range includes 0 (North) and 15 degrees
        p = HorizonPlot(altitude=(0, 40), azimuth=(-10, 30), observer=Observer())
        p.gridlines()
        assert "NORTH" in p.canvas.render()

    def test_custom_formatter_functions_are_used_for_labels(self):
        p = HorizonPlot(altitude=(0, 40), azimuth=(-10, 30), observer=Observer())
        p.gridlines(
            az_formatter_fn=lambda az: f"AZ{az}",
            alt_formatter_fn=lambda alt: f"ALT{alt}",
        )
        svg = p.canvas.render()
        assert "AZ0" in svg
        assert "AZ15" in svg

    def test_labels_false_skips_the_axes_frame_labels(self):
        p = HorizonPlot(altitude=(0, 40), azimuth=(90, 120), observer=Observer())
        p.gridlines(labels=False)
        assert p.canvas.layout.axes_frame.is_empty
