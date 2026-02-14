from starplot import geod


def test_square_simple():
    result = geod.rectangle(
        center=(200, 0),
        height_degrees=4,
        width_degrees=4,
    )
    assert result == [
        (-162.0008, -1.9996),
        (-162.0008, 1.9996),
        (-157.9992, 1.9996),
        (-157.9992, -1.9996),
    ]
    assert len(result) == 4


def test_rectangle():
    result = geod.rectangle(
        center=(50, 0),
        height_degrees=1,
        width_degrees=2,
    )
    assert result == [
        (49.0, -0.5),
        (49.0, 0.5),
        (51.0, 0.5),
        (51.0, -0.5),
    ]
    assert len(result) == 4


def test_square_at_meridian():
    result = geod.rectangle(
        center=(360, 0),
        height_degrees=4,
        width_degrees=4,
    )
    assert result == [
        (-2.0008, -1.9996),
        (-2.0008, 1.9996),
        (2.0008, 1.9996),
        (2.0008, -1.9996),
    ]
    assert len(result) == 4


def test_circle_at_meridian():
    result = geod.circle(
        center=(358, 0),
        radius_degrees=8,
        num_pts=4,
    )
    assert result == [
        (-2.0, -8.0),
        (-10.0, 0.0),
        (-2.0, 8.0),
        (6.0, 0.0),
        (-2.0, -8.0),
    ]
    assert len(result) == 5
