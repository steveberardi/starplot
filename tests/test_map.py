from datetime import UTC, datetime

import pytest

from starplot import MapPlot, Mercator, Miller, Observer, Star, _
from starplot.styles import LabelStyle


def test_map_radec_invalid():
    with pytest.raises(ValueError, match="ra_min must be less than ra_max"):
        MapPlot(
            projection=Mercator(),
            ra_min=24,
            ra_max=8,
            dec_min=-16,
            dec_max=24,
        )

    with pytest.raises(ValueError, match="dec_min must be less than dec_max"):
        MapPlot(
            projection=Mercator(),
            ra_min=8,
            ra_max=24,
            dec_min=50,
            dec_max=24,
        )


def test_map_objects_list():
    p = MapPlot(
        projection=Mercator(),
        ra_min=8.3 * 15,
        ra_max=8.8 * 15,
        dec_min=19.4,
        dec_max=19.8,
    )
    p.open_clusters()
    assert "NGC2632" in [d.name for d in p.objects.dsos]

    p.stars(where=[_.magnitude < 8])
    assert 42578 in [s.hip for s in p.objects.stars]

    assert p.objects.moon is None
    assert len(p.objects.planets) == 0


def test_map_objects_list_planets():
    dt = datetime(2023, 8, 27, 23, 0, 0, 0, tzinfo=UTC)

    p = MapPlot(
        projection=Miller(),
        ra_min=0,
        ra_max=24 * 15,
        dec_min=-40,
        dec_max=40,
        observer=Observer(dt=dt),
    )
    p.planets()
    p.sun()
    p.moon()

    assert p.objects.moon.ra == pytest.approx(291.99637857192045)
    assert p.objects.moon.dt == dt

    assert p.objects.sun.ra == pytest.approx(155.9820867071985)
    assert p.objects.sun.dt == dt

    assert len(p.objects.planets) == 8


def test_marker_no_label():
    p = MapPlot(projection=Mercator())
    p.marker(ra=150, dec=0, style__marker__fill="blue")


def test_text_no_style_kwarg():
    p = MapPlot(projection=Mercator())
    p.text(ra=100, dec=0, text="hello")


def test_plots_at_astrometric():
    """Asserts that map plots plot astrometric positions, NOT apparent"""

    barnard = Star.get(hip=87937)  # Barnard's Star
    p = MapPlot(
        projection=Miller(),
        observer=Observer.at_epoch(2000),
        ra_min=17.5 * 15,
        ra_max=18.5 * 15,
        dec_min=4,
        dec_max=5,
    )
    p.stars(where=[_.magnitude < 10])

    for s in p.objects.stars:  # find Barnard
        if s.hip == 87937:
            assert round(barnard.ra, 3) == round(s.ra, 3)
            assert round(barnard.dec, 3) == round(s.dec, 3)

    # Epoch 1991.25
    p = MapPlot(
        projection=Miller(),
        observer=Observer.at_epoch(1991.25),
        ra_min=17.5 * 15,
        ra_max=18.5 * 15,
        dec_min=4,
        dec_max=5,
    )
    p.stars(where=[_.magnitude < 10])

    for s in p.objects.stars:  # find Barnard
        if s.hip == 87937:
            assert 269.454 == round(s.ra, 3)
            assert 4.668 == round(s.dec, 3)


def _marker_plot():
    return MapPlot(
        projection=Mercator(),
        ra_min=8 * 15,
        ra_max=9 * 15,
        dec_min=10,
        dec_max=20,
    )


def test_auto_label_offset_uses_full_marker_extent():
    p = _marker_plot()
    style = LabelStyle(offset_x="auto", offset_y="auto")

    circle = p._offset_from_marker(style, "label", 20, "circle")
    crosshair = p._offset_from_marker(style, "label", 20, "circle_crosshair")
    line = p._offset_from_marker(style, "label", 20, "circle_line")

    # the crosshair is 2x its circle in both directions, so the label moves out by
    # an extra half of the circle's diameter
    assert crosshair.offset_x - circle.offset_x == pytest.approx(10 * p.scale)
    assert crosshair.offset_y - circle.offset_y == pytest.approx(10 * p.scale)

    # the line only extends horizontally
    assert line.offset_x - circle.offset_x == pytest.approx(8 * p.scale)
    assert line.offset_y == circle.offset_y


def test_marker_collision_box_uses_full_marker_extent():
    p = _marker_plot()
    ra, dec = 8.5 * 15, 15
    p.marker(
        ra=ra,
        dec=dec,
        style={"marker": {"symbol": "circle_line", "size": 20}},
    )
    x, y = p.canvas._to_display(*p._prepare_coords(ra, dec))
    half_circle = 10 * p.scale
    half_line = 18 * p.scale

    # inside the line's extent, but outside of its circle
    beyond_circle = (x + half_circle + 1, y, x + half_line - 1, y + 1)
    assert p._is_marker_collision(beyond_circle)

    # past the end of the line
    beyond_line = (x + half_line + 2, y, x + half_line + 4, y + 1)
    assert not p._is_marker_collision(beyond_line)
