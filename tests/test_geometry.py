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
