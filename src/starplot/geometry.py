import random
import math

import pyproj
import numpy as np

from shapely import union_all
from shapely.geometry import Point, Polygon, LineString

GLOBAL_EXTENT = Polygon(
    [
        [0, -90],
        [360, -90],
        [360, 90],
        [0, 90],
        [0, -90],
    ]
)

GEOD = pyproj.Geod("+a=6378137 +f=0.0", sphere=True)


def distance_m(distance_degrees: float, lat: float = 0, lon: float = 0):
    _, _, distance = GEOD.inv(lon, lat, lon + distance_degrees, lat)
    return distance


def away_from_poles(dec):
    # for some reason cartopy does not like plotting things EXACTLY at the poles
    # so, this is a little hack to avoid the bug (or maybe a misconception?) by
    # plotting a tiny bit away from the pole
    if dec == 90:
        dec -= 0.00000001
    if dec == -90:
        dec += 0.00000001

    return dec


def rectangle(
    center: tuple,
    height_degrees: float,
    width_degrees: float,
    angle: float = 0,
) -> Polygon:
    """
    Returns a rectangle polygon on a sphere, with coordinates in degrees.

    If the rectangle crosses the meridian at X=0, then the X coordinates will extend past 360.

    Args:
        center: Center of rectangle (x, y) in degrees
        height_degrees: Height of rectangle in degrees
        width_degrees: Width of rectangle in degrees
        angle: Angle to rotate rectangle, in degrees

    Returns:
        Polygon of rectangle
    """

    ra, dec = center
    dec = away_from_poles(dec)
    angle = 180 - angle

    height_m = distance_m(height_degrees)
    width_m = distance_m(width_degrees)

    distance = math.sqrt((height_m / 2) ** 2 + (width_m / 2) ** 2)
    angle_th = math.atan((height_m / 2) / (width_m / 2))

    angle_th = math.degrees(angle_th)
    points = []

    lons, lats, _ = GEOD.fwd(
        [ra] * 4,
        [dec] * 4,
        [
            angle + (90 - angle_th),
            angle + (90 + angle_th),
            angle + (270 - angle_th),
            angle + (270 + angle_th),
        ],
        [distance] * 4,
    )
    if min(lons) < 0:
        lons = [lon + 360 for lon in lons]

    points = list(zip(lons, lats))
    points = [(round(ra, 4), round(dec, 4)) for ra, dec in points]
    points.append(points[0])
    return Polygon(points)


def ellipse(
    center: tuple,
    height_degrees: float,
    width_degrees: float,
    angle: float = 0,
    num_pts: int = 100,
    start_angle: int = 0,
    end_angle: int = 360,
) -> Polygon:
    """
    Returns an ellipse polygon on a sphere, with coordinates in degrees.

    If the ellipse crosses the meridian at X=0, then the X coordinates will extend past 360.

    Args:
        center: Center of ellipse (x, y) in degrees
        height_degrees: Height of ellipse in degrees
        width_degrees: Width of ellipse in degrees
        angle: Angle to rotate ellipse, in degrees
        num_pts: Number of evenly-spaced points to generate for the ellipse. At least 100 is recommended to ensure good-looking curves.
        start_angle: Angle to start drawing the ellipse
        end_angle: Angle to stop drawing the ellipse

    Returns:
        Polygon of ellipse
    """

    ra, dec = center
    dec = away_from_poles(dec)
    angle = 180 - angle

    height = distance_m(height_degrees / 2)  # b
    width = distance_m(width_degrees / 2)  # a
    step_size = (end_angle - start_angle) / num_pts

    lons = []
    lats = []
    points = []
    for angle_pt in np.arange(start_angle, end_angle + step_size, step_size):
        radians = math.radians(angle_pt)
        radius_a = (height * width) / math.sqrt(
            height**2 * (math.sin(radians)) ** 2
            + width**2 * (math.cos(radians)) ** 2
        )
        lon, lat, _ = GEOD.fwd([ra], [dec], angle + angle_pt, radius_a)

        lons.append(lon[0])
        lats.append(lat[0])

    if min(lons) < 0:
        lons = [lon + 360 for lon in lons]

    points = list(zip(lons, lats))
    points = [(round(ra, 4), round(dec, 4)) for ra, dec in points]
    points.append(points[0])
    return Polygon(points)


def circle(center, diameter_degrees, num_pts=100) -> Polygon:
    return ellipse(
        center,
        diameter_degrees,
        diameter_degrees,
        angle=0,
        num_pts=num_pts,
    )


def union_at_zero(a: Polygon, b: Polygon) -> Polygon:
    """
    Returns union of two polygons on a sphere, with coordinates in degrees.

    If the two polygons share a border at the X=0 meridian, then the returned union will have X coordiantes that extend past 360 degrees.

    Args:
        a: First polygon
        b: Second polygon

    Returns
        Polygon union of first and second polygon
    """
    a_ra = list(a.exterior.coords.xy)[0]
    b_ra = list(b.exterior.coords.xy)[0]

    if max(a_ra) == 360 and min(b_ra) == 0:
        points = list(zip(*b.exterior.coords.xy))
        b = Polygon([[ra + 360, dec] for ra, dec in points])

    elif min(a_ra) == 0 and max(b_ra) == 360:
        points = list(zip(*a.exterior.coords.xy))
        a = Polygon([[ra + 360, dec] for ra, dec in points])

    return union_all([a, b])


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


def is_wrapped_polygon(polygon: Polygon) -> bool:
    if "MultiPolygon" == str(polygon.geom_type):
        return False

    ra, _ = [p for p in polygon.exterior.coords.xy]

    if min(ra) < 180 and max(ra) > 300:
        return True

    return False


def line_segment(start, end, step) -> list[tuple[float, float]]:
    """Returns coordinates on the line from start to end at the specified step-size"""
    return LineString([start, end]).segmentize(step).coords


class BaseGeometry:

    """
    Wrapper around shapely geometries

    Two types of polygons needed:
    1. For intersection testing: needs to be split at zero and restricted to 0-360
    2. For plotting: needs to be extended past 360 if applicable

    TODO:

        Functions
        - intersects

        Properties
        - centroid
        - bbox
        - wkt
        - wkb

    """

    def intersects(self):
        """ """
        pass
