import itertools
import math
import random

import numpy as np
import pyproj
from shapely import union_all
from shapely.errors import GEOSException
from shapely.geometry import LineString, Point, Polygon

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
            height**2 * (math.sin(radians)) ** 2 + width**2 * (math.cos(radians)) ** 2
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
    a_ra = next(iter(a.exterior.coords.xy))
    b_ra = next(iter(b.exterior.coords.xy))

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


def normalize_to_360(polygon: Polygon) -> Polygon:
    """
    If the provided polygon has coordinates with large jumps from < 100 to > 300,
    then it likely crosses the 0-point. This function will add 360 to all X coords
    under 100 and return the result.
    """

    ra, dec = [p for p in polygon.exterior.coords.xy]

    if min(ra) < 100 and max(ra) > 300:
        new_ra = [r + 360 if r < 100 else r for r in ra]
        return Polygon(list(zip(new_ra, dec)))

    return polygon


def restrict_to_360(polygon: Polygon) -> Polygon:
    """
    If the polygon has a max RA over 360, then subtract 360 from all RA coordinates.
    """
    ra, dec = [p for p in polygon.exterior.coords.xy]

    if max(ra) > 360:
        new_ra = [r - 360 for r in ra]
        return Polygon(list(zip(new_ra, dec)))

    return polygon


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
    seed: int | None = None,
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
    try:
        return LineString([start, end]).segmentize(step).coords
    except GEOSException:
        # A constellation line with one endpoint on the invisible side of a
        # hemisphere-limited projection (e.g. Orthographic) can project to
        # display coordinates that are enormously far from the other
        # endpoint, since nothing clips it before this point -- GEOS
        # refuses to segmentize a line that long at this small a step
        # ("Tolerance is too small compared to geometry length"). The line
        # is headed off-canvas either way, so just return its two
        # endpoints unsubdivided instead of crashing the whole plot.
        return [start, end]


def extend_line(
    coords: list[tuple[float, float]], distance: float
) -> list[tuple[float, float]]:
    """
    Extends a line by specific distance

    For Cartesian/planar coordinates only (e.g. display coordinates).
    """

    def extended_point(p1, p2, d):
        dx, dy = p2[0] - p1[0], p2[1] - p1[1]
        length = np.hypot(dx, dy)
        return (p2[0] + dx / length * d, p2[1] + dy / length * d)

    new_start = extended_point(coords[1], coords[0], distance)
    new_end = extended_point(coords[-2], coords[-1], distance)

    return [new_start] + coords[1:-1] + [new_end]


def split_at_antimeridian(
    coords: list[tuple[float, float]],
    antimeridian: float = 360,
    offset: float | None = 0.000001,
) -> list[list[tuple[float, float]]]:
    """
    Split a line of (x, y) coords at the antimeridian wrap point.

    If consecutive points cross from near `antimeridian` to near 0 (or vice
    versa), the line is split into separate segments at the boundary,
    interpolating the y value at the crossing point.

    Args:
        coords: List of (x, y) coordinate tuples
        antimeridian: The x-value representing the wrap boundary (e.g. 360
            for degrees, or 2*pi for radians)
        offset: Small offset applied so split segments don't land exactly on
            the boundary (avoids ambiguity at x=0/antimeridian)

    Returns:
        List of coordinate-list segments
    """
    if not coords:
        return []

    offset = offset or 0.0
    half = antimeridian / 2
    segments: list[list[tuple[float, float]]] = [[coords[0]]]

    for (x0, y0), (x1, y1) in itertools.pairwise(coords):
        dx = x1 - x0

        if dx > half:
            # e.g. x0=1, x1=350 (antimeridian=360): went 1 -> 0 -> antimeridian -> 350 (decreasing)
            wrapped = True
            going_up = False
        elif dx < -half:
            # e.g. x0=340, x1=1 (antimeridian=360): went 340 -> antimeridian -> 0 -> 1 (increasing)
            wrapped = True
            going_up = True
        else:
            wrapped = False

        if not wrapped:
            segments[-1].append((x1, y1))
            continue

        if going_up:
            # crossing from x0 up to antimeridian, then continuing from 0 up to x1
            dist_to_edge = antimeridian - x0
            total_dist = dist_to_edge + x1
            frac = dist_to_edge / total_dist if total_dist != 0 else 0
            y_cross = y0 + frac * (y1 - y0)

            segments[-1].append((antimeridian - offset, y_cross))
            segments.append([(0 + offset, y_cross), (x1, y1)])
        else:
            # crossing from x0 down to 0, then continuing from antimeridian down to x1
            dist_to_edge = x0
            total_dist = dist_to_edge + (antimeridian - x1)
            frac = dist_to_edge / total_dist if total_dist != 0 else 0
            y_cross = y0 + frac * (y1 - y0)

            segments[-1].append((0 + offset, y_cross))
            segments.append([(antimeridian - offset, y_cross), (x1, y1)])

    return segments


def split_line_at_projection_jumps(
    coords: list[tuple[float, float]],
    max_jump: float,
) -> list[list[tuple[float, float]]]:
    """
    Split a line of *already-projected* (x, y) coords wherever a point is
    non-finite or the distance from the previous point exceeds `max_jump`.

    Where a projection's discontinuity (antimeridian wraparound, a pole
    singularity, etc.) actually falls in raw data (e.g. RA/DEC) space depends
    on the projection -- for a plain cylindrical projection it's a fixed
    meridian, but for a rotated one (e.g. oblique Mercator) it's a curve that
    isn't expressible as a single coordinate value. Rather than compute that
    curve analytically per-projection, this projects first and cuts wherever
    the *output* actually jumps or blows up, which works the same way for
    every projection.

    Args:
        coords: List of already-projected (x, y) coordinate tuples
        max_jump: Distance threshold (in projected units) above which two
            consecutive points are considered discontinuous

    Returns:
        List of coordinate-list segments
    """
    if not coords:
        return []

    segments = []
    current = []

    for x, y in coords:
        if not (math.isfinite(x) and math.isfinite(y)):
            if current:
                segments.append(current)
                current = []
            continue

        if current:
            px, py = current[-1]
            if math.hypot(x - px, y - py) > max_jump:
                segments.append(current)
                current = []

        current.append((x, y))

    if current:
        segments.append(current)

    return segments


def split_ring_at_projection_jumps(
    coords: list[tuple[float, float]],
    max_jump: float,
) -> list[list[tuple[float, float]]]:
    """
    Like `split_line_at_projection_jumps`, but for a *closed* ring (e.g. a
    polygon's exterior). Treats the sequence as cyclic, so an arc that wraps
    across the start/end of the coordinate list comes back as a single
    piece instead of being cut in two at an arbitrary array boundary.

    Args:
        coords: List of already-projected (x, y) ring coordinates (first and
            last points may or may not repeat -- both are handled)
        max_jump: Distance threshold (in projected units) above which two
            consecutive points are considered discontinuous

    Returns:
        List of coordinate-list arcs. Empty if the ring has fewer than 3
        distinct points.
    """
    pts = coords[:-1] if len(coords) > 1 and coords[0] == coords[-1] else list(coords)
    n = len(pts)
    if n < 3:
        return []

    def finite(p):
        return math.isfinite(p[0]) and math.isfinite(p[1])

    jump_after = [
        i
        for i in range(n)
        if not (finite(pts[i]) and finite(pts[(i + 1) % n]))
        or math.hypot(pts[(i + 1) % n][0] - pts[i][0], pts[(i + 1) % n][1] - pts[i][1])
        > max_jump
    ]
    if not jump_after:
        return [pts]

    start = (jump_after[0] + 1) % n
    rotated = [pts[(start + k) % n] for k in range(n)]
    return split_line_at_projection_jumps(rotated, max_jump)


def angular_distance(ra1: float, dec1: float, ra2: float, dec2: float) -> float:
    """Great-circle angular distance between two RA/DEC points, in degrees."""
    ra1, dec1, ra2, dec2 = (math.radians(v) for v in (ra1, dec1, ra2, dec2))
    cos_c = math.sin(dec1) * math.sin(dec2) + math.cos(dec1) * math.cos(
        dec2
    ) * math.cos(ra1 - ra2)
    cos_c = max(-1.0, min(1.0, cos_c))  # guard float rounding at +/-1
    return math.degrees(math.acos(cos_c))


def split_line_at_horizon(
    coords: list[tuple[float, float]],
    center: tuple[float, float],
    max_angular_distance: float,
) -> list[list[tuple[float, float]]]:
    """
    Split a line of *raw* (ra, dec) coords wherever a point falls beyond
    max_angular_distance from center -- for hemisphere-limited projections
    (e.g. Orthographic), where PROJ maps a point just beyond the horizon
    to a finite location close to its visible neighbor (mirrored back onto
    the visible disc) rather than a jump or a non-finite value, so
    split_line_at_projection_jumps -- which only looks at the *projected*
    output -- can't detect the cut on its own. This runs first, in RA/DEC
    space, before projecting.

    Args:
        coords: List of raw (ra, dec) coordinate tuples
        center: The projection's (center_ra, center_dec)
        max_angular_distance: Points farther than this from center (in
            degrees) are dropped

    Returns:
        List of coordinate-list segments
    """
    if not coords:
        return []

    center_ra, center_dec = center
    segments = []
    current = []

    for ra, dec in coords:
        if angular_distance(ra, dec, center_ra, center_dec) <= max_angular_distance:
            current.append((ra, dec))
        elif current:
            segments.append(current)
            current = []

    if current:
        segments.append(current)

    return segments


def split_ring_at_horizon(
    coords: list[tuple[float, float]],
    center: tuple[float, float],
    max_angular_distance: float,
) -> list[list[tuple[float, float]]]:
    """
    Like `split_line_at_horizon`, but for a *closed* ring. Treats the
    sequence as cyclic, so an arc that wraps across the start/end of the
    coordinate list comes back as a single piece instead of being cut in
    two at an arbitrary array boundary.

    Returns:
        List of coordinate-list arcs. Empty if nothing is visible.
    """
    pts = coords[:-1] if len(coords) > 1 and coords[0] == coords[-1] else list(coords)
    n = len(pts)
    if n < 3:
        return []

    center_ra, center_dec = center
    visible = [
        angular_distance(ra, dec, center_ra, center_dec) <= max_angular_distance
        for ra, dec in pts
    ]

    if all(visible):
        return [pts]
    if not any(visible):
        return []

    cut_after = [i for i in range(n) if visible[i] and not visible[(i + 1) % n]]
    start = (cut_after[0] + 1) % n
    rotated = [pts[(start + k) % n] for k in range(n)]
    return split_line_at_horizon(rotated, center, max_angular_distance)


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


# class BaseGeometry:
#     """
#     Wrapper around shapely geometries

#     Two types of polygons needed:
#     1. For intersection testing: needs to be split at zero and restricted to 0-360
#     2. For plotting: needs to be extended past 360 if applicable

#     TODO:

#         Functions
#         - intersects

#         Properties
#         - centroid
#         - bbox
#         - wkt
#         - wkb

#     """

#     def intersects(self):
#         """TODO"""
