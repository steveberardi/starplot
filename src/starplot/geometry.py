import random

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
