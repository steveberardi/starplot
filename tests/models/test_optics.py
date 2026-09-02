import math

import pytest

from starplot.models.optics import Binoculars, Camera, Reflector, Refractor, Scope


class TestScope:
    def test_magnification(self):
        s = Scope(focal_length=1000, eyepiece_focal_length=10, eyepiece_fov=50)
        assert s.magnification == 100.0

    def test_true_fov(self):
        s = Scope(focal_length=1000, eyepiece_focal_length=10, eyepiece_fov=50)
        assert s.true_fov == 0.5

    def test_radius_derives_from_true_fov(self):
        s = Scope(focal_length=1000, eyepiece_focal_length=10, eyepiece_fov=50)
        assert s.radius == s._compute_radius(s.true_fov / 2)

    def test_label_and_str(self):
        s = Scope(focal_length=1000, eyepiece_focal_length=10, eyepiece_fov=50)
        assert s.label == "Scope"
        assert (
            str(s)
            == "1000mm w/ 10mm (100x) @  50\N{DEGREE SIGN} = 0.50\N{DEGREE SIGN} TFOV"
        )

    def test_does_not_invert_by_default(self):
        s = Scope(focal_length=1000, eyepiece_focal_length=10, eyepiece_fov=50)
        assert s.invert_x is False
        assert s.invert_y is False

    def test_polygon_is_centered_with_true_fov_extent(self):
        s = Scope(focal_length=1000, eyepiece_focal_length=10, eyepiece_fov=50)
        poly = s.polygon(10, 20)
        assert poly.centroid.x == pytest.approx(10, abs=1e-6)
        assert poly.centroid.y == pytest.approx(20, abs=1e-3)
        minx, _, maxx, _ = poly.bounds
        assert maxx - minx == pytest.approx(s.true_fov, rel=0.1)

    def test_in_bounds_at_the_radius_boundary(self):
        s = Scope(focal_length=1000, eyepiece_focal_length=10, eyepiece_fov=50)
        assert s.in_bounds(0, 0) is True
        assert s.in_bounds(s.radius * 0.99, 0) is True
        assert s.in_bounds(s.radius * 1.01, 0) is False

    def test_in_bounds_scales_the_radius(self):
        s = Scope(focal_length=1000, eyepiece_focal_length=10, eyepiece_fov=50)
        # a point just outside the unscaled radius comes back into bounds
        # once the radius is scaled up
        assert s.in_bounds(s.radius * 1.5, 0, scale=1) is False
        assert s.in_bounds(s.radius * 1.5, 0, scale=2) is True


class TestRefractor:
    def test_inverts_x_only(self):
        r = Refractor(focal_length=1000, eyepiece_focal_length=10, eyepiece_fov=50)
        assert r.invert_x is True
        assert r.invert_y is False

    def test_label(self):
        r = Refractor(focal_length=1000, eyepiece_focal_length=10, eyepiece_fov=50)
        assert r.label == "Refractor"


class TestReflector:
    def test_inverts_both_axes(self):
        r = Reflector(focal_length=1000, eyepiece_focal_length=10, eyepiece_fov=50)
        assert r.invert_x is True
        assert r.invert_y is True

    def test_label(self):
        r = Reflector(focal_length=1000, eyepiece_focal_length=10, eyepiece_fov=50)
        assert r.label == "Reflector"


class TestBinoculars:
    def test_true_fov(self):
        b = Binoculars(magnification=10, fov=65)
        assert b.true_fov == 6.5

    def test_radius_derives_from_true_fov(self):
        b = Binoculars(magnification=10, fov=65)
        assert b.radius == b._compute_radius(b.true_fov / 2)

    def test_label(self):
        b = Binoculars(magnification=10, fov=65)
        assert b.label == "Binoculars"

    def test_polygon_is_centered_with_true_fov_extent(self):
        b = Binoculars(magnification=10, fov=65)
        # RA=90 avoids both the 0/360 seam and the antimeridian (RA 180),
        # where geometry.circle()'s wraparound handling has known issues
        poly = b.polygon(90, 0)
        assert poly.centroid.x == pytest.approx(90, abs=1e-6)
        minx, _, maxx, _ = poly.bounds
        assert maxx - minx == pytest.approx(b.true_fov, rel=0.1)

    def test_in_bounds_at_the_radius_boundary(self):
        b = Binoculars(magnification=10, fov=65)
        assert b.in_bounds(b.radius * 0.99, 0) is True
        assert b.in_bounds(b.radius * 1.01, 0) is False


class TestCamera:
    def test_true_fov_x_and_y_from_sensor_dimensions(self):
        c = Camera(sensor_width=36, sensor_height=24, lens_focal_length=50)
        # TFOV = 2 * arctan(d / (2 * f)), independently derived from the
        # documented formula rather than copied from the implementation
        expected_x = 2 * math.degrees(math.atan(36 / (2 * 50)))
        expected_y = 2 * math.degrees(math.atan(24 / (2 * 50)))
        assert c.true_fov_x == pytest.approx(expected_x)
        assert c.true_fov_y == pytest.approx(expected_y)

    def test_true_fov_is_the_larger_of_the_two_axes(self):
        wide = Camera(sensor_width=36, sensor_height=24, lens_focal_length=50)
        assert wide.true_fov == wide.true_fov_x

        tall = Camera(sensor_width=24, sensor_height=36, lens_focal_length=50)
        assert tall.true_fov == tall.true_fov_y

    def test_radius_x_and_y_derive_from_their_respective_fov(self):
        c = Camera(sensor_width=36, sensor_height=24, lens_focal_length=50)
        assert c.radius_x == c._compute_radius(c.true_fov_x / 2)
        assert c.radius_y == c._compute_radius(c.true_fov_y / 2)

    def test_label(self):
        c = Camera(sensor_width=36, sensor_height=24, lens_focal_length=50)
        assert c.label == "Camera"

    def test_polygon_extent_matches_sensor_aspect_ratio(self):
        c = Camera(sensor_width=36, sensor_height=24, lens_focal_length=50)
        poly = c.polygon(5, 5)
        minx, miny, maxx, maxy = poly.bounds
        assert maxx - minx == pytest.approx(c.true_fov_x, rel=0.1)
        assert maxy - miny == pytest.approx(c.true_fov_y, rel=0.1)

    def test_in_bounds_with_no_rotation(self):
        c = Camera(sensor_width=36, sensor_height=24, lens_focal_length=50, rotation=0)
        assert c.in_bounds(c.radius_x * 0.9, 0) is True
        assert c.in_bounds(c.radius_x * 1.1, 0) is False
        assert c.in_bounds(0, c.radius_y * 0.9) is True
        assert c.in_bounds(0, c.radius_y * 1.1) is False

    def test_rotation_swaps_which_axis_each_radius_applies_to(self):
        # a wide sensor, so radius_x and radius_y are clearly different
        unrotated = Camera(
            sensor_width=36, sensor_height=24, lens_focal_length=50, rotation=0
        )
        rotated = Camera(
            sensor_width=36, sensor_height=24, lens_focal_length=50, rotation=90
        )
        point = (unrotated.radius_x * 0.9, 0)

        # in bounds along the (wider) x-axis when unrotated...
        assert unrotated.in_bounds(*point) is True
        # ...but the same point falls outside once the frame is rotated 90
        # degrees, since that point now exceeds the (narrower) y radius
        assert rotated.in_bounds(*point) is False
