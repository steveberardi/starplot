from itertools import pairwise

from starplot import geometry


def test_square_simple():
    polygon = geometry.rectangle(
        center=(200, 0),
        height_degrees=4,
        width_degrees=4,
    )
    points = list(zip(*polygon.exterior.coords.xy))
    assert points == [
        (197.9992, -1.9996),
        (197.9992, 1.9996),
        (202.0008, 1.9996),
        (202.0008, -1.9996),
        (197.9992, -1.9996),
    ]
    assert len(points) == 5


def test_rectangle():
    polygon = geometry.rectangle(
        center=(50, 0),
        height_degrees=1,
        width_degrees=2,
    )
    points = list(zip(*polygon.exterior.coords.xy))
    assert points == [
        (49.0, -0.5),
        (49.0, 0.5),
        (51.0, 0.5),
        (51.0, -0.5),
        (49.0, -0.5),
    ]
    assert len(points) == 5


def test_square_at_meridian():
    polygon = geometry.rectangle(
        center=(360, 0),
        height_degrees=4,
        width_degrees=4,
    )
    points = list(zip(*polygon.exterior.coords.xy))
    assert points == [
        (357.9992, -1.9996),
        (357.9992, 1.9996),
        (362.0008, 1.9996),
        (362.0008, -1.9996),
        (357.9992, -1.9996),
    ]
    assert len(points) == 5


def test_circle_at_meridian():
    polygon = geometry.circle(
        center=(358, 0),
        diameter_degrees=16,
        num_pts=4,
    )
    points = list(zip(*polygon.exterior.coords.xy))
    assert points == [
        (358.0, -8.0),
        (350.0, 0.0),
        (358.0, 8.0),
        (366.0, 0.0),
        (358.0, -8.0),
        (358.0, -8.0),
    ]
    assert len(points) == 6


def test_square_at_antimeridian():
    polygon = geometry.rectangle(
        center=(180, 0),
        height_degrees=4,
        width_degrees=4,
    )
    points = list(zip(*polygon.exterior.coords.xy))
    assert points == [
        (177.9992, -1.9996),
        (177.9992, 1.9996),
        (182.0008, 1.9996),
        (182.0008, -1.9996),
        (177.9992, -1.9996),
    ]


def test_circle_at_antimeridian():
    polygon = geometry.circle(
        center=(180, 0),
        diameter_degrees=16,
        num_pts=4,
    )
    points = list(zip(*polygon.exterior.coords.xy))
    assert points == [
        (180.0, -8.0),
        (172.0, 0.0),
        (180.0, 8.0),
        (188.0, 0.0),
        (180.0, -8.0),
        (180.0, -8.0),
    ]


def test_ellipse_is_on_ellipse_and_dense_at_tips():
    # equator, so degrees of RA/dec are ~equal distances
    polygon = geometry.ellipse((180, 0), height_degrees=1, width_degrees=4, num_pts=100)
    points = list(zip(*polygon.exterior.coords.xy))
    for x, y in points:
        assert abs(((x - 180) / 2) ** 2 + (y / 0.5) ** 2 - 1) < 0.01

    # points at the sharp tips (|x - 180| > 1.8) should be spaced closer than
    # points along the flat sides
    gaps = [
        (abs(x1 - 180), ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5)
        for (x1, y1), (x2, y2) in pairwise(points)
    ]
    tip = max(g for x, g in gaps if x > 1.8)
    side = max(g for x, g in gaps if x < 1.0)
    assert tip < side


def test_ellipse_circle_radius():
    polygon = geometry.circle((180, 0), 2)
    for x, y in zip(*polygon.exterior.coords.xy):
        assert abs((x - 180) ** 2 + y**2 - 1) < 0.01
