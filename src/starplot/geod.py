import math

import pyproj


GEOD = pyproj.Geod("+a=6378137 +f=0.0", sphere=True)


def distance_m(distance_degrees: float, lat: float = 0, lon: float = 0):
    _, _, distance = GEOD.inv(lon, lat, lon + distance_degrees, lat)
    return distance


def to_radec(p) -> tuple:
    return (p[0] / 15, p[1])


def rectangle(
    center: tuple,
    height_degrees: float,
    width_degrees: float,
    angle: float = 0,
) -> list:
    ra, dec = center
    ra = ra * 15
    angle = 180 - angle

    if dec == 90:
        dec -= 0.00000001
    if dec == -90:
        dec += 0.00000001

    height_m = distance_m(height_degrees)
    width_m = distance_m(width_degrees)

    c = math.sqrt((height_m / 2) ** 2 + (width_m / 2) ** 2)
    angle_th = math.atan((height_m / 2) / (width_m / 2))

    angle_th = math.degrees(angle_th)
    points = []

    p0_lon, p0_lat, _ = GEOD.fwd([ra], [dec], angle + (90 - angle_th), c)
    p1_lon, p1_lat, _ = GEOD.fwd([ra], [dec], angle + (90 + angle_th), c)
    p2_lon, p2_lat, _ = GEOD.fwd([ra], [dec], angle + (270 - angle_th), c)
    p3_lon, p3_lat, _ = GEOD.fwd([ra], [dec], angle + (270 + angle_th), c)

    points.append((p0_lon[0], p0_lat[0]))
    points.append((p1_lon[0], p1_lat[0]))
    points.append((p2_lon[0], p2_lat[0]))
    points.append((p3_lon[0], p3_lat[0]))

    return points


def ellipse(
    center: tuple,
    height_degrees: float,
    width_degrees: float,
    angle: float = 0,
    num_pts: int = 100,
) -> list:
    ra, dec = center
    ra = ra * 15
    angle = 180 - angle

    if dec == 90:
        dec -= 0.00000001
    if dec == -90:
        dec += 0.00000001

    height = distance_m(height_degrees / 2)  # b
    width = distance_m(width_degrees / 2)  # a

    points = []
    for angle_pt in range(0, 360, int(360 / num_pts)):
        radians = math.radians(angle_pt)
        radius_a = (height * width) / math.sqrt(
            height**2 * (math.sin(radians)) ** 2
            + width**2 * (math.cos(radians)) ** 2
        )
        lon, lat, _ = GEOD.fwd([ra], [dec], angle + angle_pt, radius_a)

        points.append((lon[0], lat[0]))

    return points


def circle(center: tuple, radius_degrees: float, num_pts: int = 100) -> list:
    return ellipse(
        center,
        radius_degrees * 2,
        radius_degrees * 2,
        angle=0,
        num_pts=num_pts,
    )
