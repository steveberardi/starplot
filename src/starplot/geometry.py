import random
import math

from shapely.geometry import Point, Polygon


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


def wrapped_polygon_adjustment(polygon: Polygon) -> int:
    if "MultiPolygon" == str(polygon.geom_type):
        return 0

    points = list(zip(*polygon.exterior.coords.xy))
    prev = None

    for ra, _ in points:
        if prev is not None and prev > 20 and ra < 12:
            return 24
        elif prev is not None and prev < 12 and ra > 20:
            return -24
        prev = ra

    return 0
