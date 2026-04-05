import random
import math

import pyproj
import numpy as np

from shapely import union_all
from shapely.geometry import Point, Polygon, LineString

from starplot.constants import PROJ_R

GLOBAL_EXTENT = Polygon(
    [
        [0, -90],
        [360, -90],
        [360, 90],
        [0, 90],
        [0, -90],
    ]
)

GEOD = pyproj.Geod(f"+a={PROJ_R} +f=0.0", sphere=True)


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


def split_line_at_meridian(p1, p2, meridian=360):
    """Split a line that crosses the meridian into two segments."""
    x1, y1 = p1
    x2, y2 = p2

    # Interpolate the crossing point
    t = (meridian - x1) / (x2 - x1)
    y_cross = y1 + t * (y2 - y1)

    # Two segments on either side
    seg1 = [(x1, y1), (359.9999999, y_cross)]
    seg2 = [
        (0.0000001, y_cross),
        (x2 - 360, y2),
    ]  # or -meridian depending on convention

    return seg1, seg2


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


def split_line_at_x(
    coords: list[tuple[float, float]],
    split_x: float,
    offset: float | None = 0.000001,
) -> list[list[tuple]]:
    """
    Split a list of (x, y) coords at a specific x value.
    Returns a list of segments (each a list of (x, y) tuples).

    If offset is provided, the split points are nudged away from split_x on each side.
    """
    segments = []
    current = [coords[0]]

    for i in range(1, len(coords)):
        x1, y1 = current[-1]
        x2, y2 = coords[i]

        if ((x1 <= split_x <= x2) or (x2 <= split_x <= x1)) and x1 != x2:
            t = (split_x - x1) / (x2 - x1)
            y_cross = y1 + t * (y2 - y1)

            if offset is not None:
                # Nudge each end away from split_x
                end_x = split_x - offset if x1 <= split_x else split_x + offset
                start_x = split_x + offset if x1 <= split_x else split_x - offset
            else:
                end_x = split_x
                start_x = split_x

            current.append((end_x, y_cross))
            segments.append(current)
            current = [(start_x, y_cross), (x2, y2)]
        else:
            current.append((x2, y2))

    if len(current) >= 2:
        segments.append(current)

    return segments


def extent_polygon(
    min_x: float,
    max_x: float,
    min_y: float,
    max_y: float,
    n: int = 100,
) -> np.ndarray:
    """
    Build a polygon around an extent by sampling n points along each edge.
    Returns an (4n, 2) array of (x, y) coordinates in order:
    bottom → right → top → left
    """
    xs_bottom = np.linspace(min_x, max_x, n)
    xs_top = np.linspace(max_x, min_x, n)  # reversed to close polygon CCW
    ys_left = np.linspace(min_y, max_y, n)
    ys_right = np.linspace(max_y, min_y, n)  # reversed

    bottom = np.column_stack([xs_bottom, np.full(n, min_y)])
    right = np.column_stack([np.full(n, max_x), ys_left])
    top = np.column_stack([xs_top, np.full(n, max_y)])
    left = np.column_stack([np.full(n, min_x), ys_right])

    return np.vstack([bottom, right, top, left])


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
