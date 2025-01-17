import random
import math
from typing import Union

from shapely import transform
from shapely.geometry import Point, Polygon, MultiPolygon

from starplot import geod, utils

GLOBAL_EXTENT = Polygon(
    [
        [0, -90],
        [360, -90],
        [360, 90],
        [0, 90],
        [0, -90],
    ]
)


def circle(center, diameter_degrees):
    points = geod.ellipse(
        center,
        diameter_degrees,
        diameter_degrees,
        angle=0,
        num_pts=100,
    )
    points = [
        (round(24 - utils.lon_to_ra(lon), 4), round(dec, 4)) for lon, dec in points
    ]
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
