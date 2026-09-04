from starplot import GalaxyPlot, Observer
from starplot.svg.elements import Group, Polyline


def test_default_center_lon_is_zero():
    p = GalaxyPlot()
    assert p.center_lon == 0


def test_extent_always_covers_the_whole_sky():
    p = GalaxyPlot(observer=Observer(lat=32.97, lon=-117.038611))
    assert p.ra_min == 0
    assert p.ra_max == 360
    assert p.dec_min == -90
    assert p.dec_max == 90


def test_ra_above_360_wraps_to_the_same_result():
    p = GalaxyPlot()
    assert p._prepare_coords(370, 10) == p._prepare_coords(10, 10)


def test_ra_below_zero_wraps_to_the_same_result():
    p = GalaxyPlot()
    assert p._prepare_coords(-350, 10) == p._prepare_coords(10, 10)


def test_point_within_axes_is_in_bounds():
    p = GalaxyPlot()
    assert p.in_bounds_lonlat(0, 0) is True


def test_point_far_outside_axes_is_not_in_bounds():
    p = GalaxyPlot()
    assert p.in_bounds_lonlat(1000, 1000) is False


def test_in_bounds_matches_in_bounds_lonlat_of_the_prepared_coords():
    p = GalaxyPlot()
    lon, lat = p._prepare_coords(10, 10)
    assert p.in_bounds(10, 10) == p.in_bounds_lonlat(lon, lat)


def test_in_bounds_ra_wraparound_is_consistent():
    p = GalaxyPlot()
    assert p.in_bounds(370, 10) == p.in_bounds(10, 10)


def test_adds_polylines_to_the_canvas():
    p = GalaxyPlot()
    before = [e for _, e in p.canvas.layout.axes.elements if isinstance(e, Polyline)]
    assert before == []

    p.galactic_equator()

    after = [e for _, e in p.canvas.layout.axes.elements if isinstance(e, Polyline)]
    assert len(after) > 0


def test_default_label_is_rendered():
    p = GalaxyPlot()
    p.galactic_equator()
    assert "GALACTIC EQUATOR" in p.canvas.render()


def test_custom_label_is_rendered():
    p = GalaxyPlot()
    p.galactic_equator(label="EQ")
    assert "EQ" in p.canvas.render()


def test_adds_a_group_of_polylines_to_the_canvas():
    p = GalaxyPlot()
    before = [e for _, e in p.canvas.layout.axes.elements if isinstance(e, Group)]
    assert before == []

    p.gridlines()

    groups = [e for _, e in p.canvas.layout.axes.elements if isinstance(e, Group)]
    assert len(groups) == 1
    assert groups[0].id == "gridlines"
    assert len(groups[0].children) > 0
    assert all(isinstance(c, Polyline) for c in groups[0].children)


def test_default_lon_label_is_rendered():
    p = GalaxyPlot()
    p.gridlines()
    assert "0°" in p.canvas.render()


def test_custom_formatter_function_is_used_for_labels():
    p = GalaxyPlot()
    p.gridlines(lon_formatter_fn=lambda lon: f"LON{lon}")
    assert "LON0" in p.canvas.render()


def test_lat_labels_are_rendered():
    # in the Mollweide projection, a latitude gridline touches the axes
    # border at the antimeridian (mid-array), not at its own coordinate
    # array's start/end -- regression test for a bug where that meant no
    # lat label ever registered a border intersection at all
    p = GalaxyPlot()
    p.gridlines(lat_formatter_fn=lambda lat: f"LAT{lat}")
    svg = p.canvas.render()
    assert "LAT0" in svg
    assert "LAT30" in svg
    assert "LAT-30" in svg


def test_labels_false_skips_the_axes_frame_labels():
    p = GalaxyPlot()
    p.gridlines(labels=False)
    assert p.canvas.layout.axes_frame.is_empty


def test_labels_true_populates_the_axes_frame():
    p = GalaxyPlot()
    p.gridlines(labels=True)
    assert not p.canvas.layout.axes_frame.is_empty
