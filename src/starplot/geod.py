import math

import pyproj
import numpy as np

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
) -> list:
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
    points = list(zip(lons, lats))

    return [(round(ra, 4), round(dec, 4)) for ra, dec in points]


def ellipse(
    center: tuple,
    height_degrees: float,
    width_degrees: float,
    angle: float = 0,
    num_pts: int = 100,
    start_angle: int = 0,
    end_angle: int = 360,
) -> list:
    ra, dec = center
    dec = away_from_poles(dec)
    angle = 180 - angle

    height = distance_m(height_degrees / 2)  # b
    width = distance_m(width_degrees / 2)  # a
    step_size = (end_angle - start_angle) / num_pts

    points = []
    for angle_pt in np.arange(start_angle, end_angle + step_size, step_size):
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
