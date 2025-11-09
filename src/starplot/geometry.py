import random
import math
from typing import Union

from shapely import transform
from shapely.geometry import Point, Polygon, MultiPolygon

from starplot import geod

GLOBAL_EXTENT = Polygon(
    [
        [0, -90],
        [360, -90],
        [360, 90],
        [0, 90],
        [0, -90],
    ]
)


def circle(center, diameter_degrees, num_pts=100):
    points = geod.ellipse(
        center,
        diameter_degrees,
        diameter_degrees,
        angle=0,
        num_pts=num_pts,
    )
    # points = [
    #     (round(24 - utils.lon_to_ra(lon), 4), round(dec, 4)) for lon, dec in points
    # ]
    points = [(round(lon, 4), round(dec, 4)) for lon, dec in points]
    return Polygon(points)


def to_24h(geometry: Union[Point, Polygon, MultiPolygon]):
    geometry_type = str(geometry.geom_type)

    if geometry_type == "MultiPolygon":
        polygons = [transform(p, lambda c: c * [1 / 15, 1]) for p in geometry.geoms]
        return MultiPolygon(polygons)

    return transform(geometry, lambda c: c * [1 / 15, 1])


def unwrap_polygon(polygon: Polygon) -> Polygon:
    points = list(zip(*polygon.exterior.coords.xy))
    new_points = []
    prev = None

    for x, y in points:
        if prev is not None and prev > 20 and x < 12:
            x += 24
        elif prev is not None and prev < 12 and x > 20:
            x -= 24
        new_points.append((x, y))
        prev = x

    return Polygon(new_points)


def unwrap_polygon_360_old(polygon: Polygon) -> Polygon:
    points = list(zip(*polygon.exterior.coords.xy))
    new_points = []
    prev = None

    for x, y in points:
        if prev is not None and prev > 300 and x < 180:
            x -= 360
        elif prev is not None and prev < 180 and x > 300:
            x += 360
        new_points.append((x, y))
        prev = x

    return Polygon(new_points)


def unwrap_polygon_360_inverse(polygon: Polygon) -> Polygon:
    ra, dec = [p for p in polygon.exterior.coords.xy]

    if min(ra) < 180 and max(ra) > 300:
        new_ra = [r + 360 if r < 50 else r for r in ra]
        points = list(zip(new_ra, dec))
        return Polygon(points)

    return polygon


def unwrap_polygon_360(polygon: Polygon) -> Polygon:
    ra, dec = [p for p in polygon.exterior.coords.xy]

    if min(ra) < 180 and max(ra) > 300:
        new_ra = [r - 360 if r > 300 else r for r in ra]
        return Polygon(list(zip(new_ra, dec)))

    return polygon


def split_polygon_at_zero(polygon: Polygon) -> list[Polygon]:
    """
    Splits a polygon at the first point of Aries (RA=0)

    Args:
        polygon: Polygon that possibly needs splitting

    Returns:
        List of polygons
    """
    ra, dec = [p for p in polygon.exterior.coords.xy]

    if min(ra) < 180 and max(ra) > 300:
        new_ra = [r + 360 if r < 180 else r for r in ra]
        new_polygon = Polygon(list(zip(new_ra, dec)))

        polygon_1 = new_polygon.intersection(
            Polygon(
                [
                    [0, -90],
                    [360, -90],
                    [360, 90],
                    [0, 90],
                    [0, -90],
                ]
            )
        )

        polygon_2 = new_polygon.intersection(
            Polygon(
                [
                    [360, -90],
                    [720, -90],
                    [720, 90],
                    [360, 90],
                    [360, -90],
                ]
            )
        )

        p2_ra, p2_dec = [p for p in polygon_2.exterior.coords.xy]
        p2_new_ra = [ra - 360 for ra in p2_ra]

        return [polygon_1, Polygon(list(zip(p2_new_ra, p2_dec)))]

    return [polygon]


def split_polygon_at_360(polygon: Polygon) -> list[Polygon]:
    """
    Splits a polygon at 360 degrees

    Args:
        polygon: Polygon that possibly needs splitting

    Returns:
        List of polygons
    """
    ra, _ = [p for p in polygon.exterior.coords.xy]

    if max(ra) > 360:
        polygon_1 = polygon.intersection(
            Polygon(
                [
                    [0, -90],
                    [360, -90],
                    [360, 90],
                    [0, 90],
                    [0, -90],
                ]
            )
        )

        polygon_2 = polygon.intersection(
            Polygon(
                [
                    [360, -90],
                    [720, -90],
                    [720, 90],
                    [360, 90],
                    [360, -90],
                ]
            )
        )

        p2_ra, p2_dec = [p for p in polygon_2.exterior.coords.xy]
        p2_new_ra = [ra - 360 for ra in p2_ra]

        return [polygon_1, Polygon(list(zip(p2_new_ra, p2_dec)))]

    return [polygon]


def random_point_in_polygon(
    polygon: Polygon, max_iterations: int = 100, seed: int = None
) -> Point:
    """Returns a random point inside a shapely polygon"""
    if seed:
        random.seed(seed)

    ctr = 0
    x0, y0, x1, y1 = polygon.bounds

    while ctr < max_iterations:
        x = random.uniform(x0, x1)
        y = random.uniform(y0, y1)
        point = Point(x, y)
        if polygon.contains(point):
            return point

    return None


def random_point_in_polygon_at_distance(
    polygon: Polygon,
    origin_point: Point,
    distance: int,
    max_iterations: int = 100,
    seed: int = None,
) -> Point:
    """Returns a random point inside a polygon, at a specified distance from the origin point"""
    if seed:
        random.seed(seed)

    ctr = 0
    while ctr < max_iterations:
        ctr += 1
        angle = random.uniform(0, 2 * math.pi)
        x = origin_point.x + distance * math.cos(angle)
        y = origin_point.y + distance * math.sin(angle)
        point = Point(x, y)

        if polygon.contains(point):
            return point

    return None


def wrapped_polygon_adjustment_old(polygon: Polygon) -> int:
    if "MultiPolygon" == str(polygon.geom_type):
        return 0

    points = list(zip(*polygon.exterior.coords.xy))
    prev = None

    for ra, _ in points:
        if prev is not None and prev > 300 and ra < 180:
            return 360
        elif prev is not None and prev < 180 and ra > 300:
            return -360
        prev = ra

    return 0


def wrapped_polygon_adjustment(polygon: Polygon) -> int:
    if "MultiPolygon" == str(polygon.geom_type):
        return 0

    ra, _ = [p for p in polygon.exterior.coords.xy]

    if min(ra) < 180 and max(ra) > 300:
        return 360

    return 0


def is_wrapped_polygon(polygon: Polygon) -> bool:
    if "MultiPolygon" == str(polygon.geom_type):
        return False

    ra, _ = [p for p in polygon.exterior.coords.xy]

    if min(ra) < 180 and max(ra) > 300:
        return True

    return False
