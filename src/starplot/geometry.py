import random
import math

from shapely.geometry import Point, Polygon


def random_point_in_polygon(polygon: Polygon) -> Point:
    """Returns a random point inside a shapely polygon"""
    minx, miny, maxx, maxy = polygon.bounds
    while True:
        x = random.uniform(minx, maxx)
        y = random.uniform(miny, maxy)
        point = Point(x, y)
        if polygon.contains(point):
            return point


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


def random_point_in_polygon_at_distance(
    polygon: Polygon, origin_point: Point, distance: int, max_iterations: int = 100
) -> Point:
    ctr = 0
    while ctr < max_iterations:
        ctr += 1

        angle = random.uniform(0, 2 * math.pi)
        new_x = origin_point.x + distance * math.cos(angle)
        new_y = origin_point.y + distance * math.sin(angle)
        new_point = Point(new_x, new_y)

        if polygon.contains(new_point):
            return new_point

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
