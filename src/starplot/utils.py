import math
from datetime import datetime

import numpy as np
from pytz import timezone


def in_circle(x, y, center_x=0, center_y=0, radius=0.9) -> bool:
    """Determine if a point (x,y) is inside a circle"""
    return (x - center_x) ** 2 + (y - center_y) ** 2 < (radius**2)


def lon_to_ra(lon: float):
    pos_lon = lon + 180
    ra = 12 - (24 * pos_lon / 360)
    if ra < 0:
        ra += 24
    return ra


def ra_to_lon(ra):
    lon = ra * -15
    if lon < -180:
        lon += 360

    return lon


def lon_to_ra_hms(lon: float) -> (int, int, int):
    """Converts longitude back to right ascension

    Args:
        lon: Longitude to convert

    Returns:
        Tuple of ints: (hours, minutes, seconds)
    """
    pos_lon = lon + 180
    ra_decimal = 12 - (24 * pos_lon / 360)

    hour = math.floor(ra_decimal)

    min_decimal = 60 * (ra_decimal - hour)
    minutes = math.floor(min_decimal)

    sec_decimal = 60 * (min_decimal - minutes)
    seconds = math.floor(sec_decimal)

    if hour < 0:
        hour += 24

    if seconds >= 60:
        minutes += 1
        seconds -= 60

    return hour, minutes, seconds


def dec_str_to_float(dec_str):
    """
    Converts declination strings to a single float:

    >> dec_str_to_float("-05:20:30")
    >> -5.341667

    """
    multiplier = 1
    dec_d, dec_m, dec_s = [float(d) for d in dec_str.split(":")]

    if dec_str.startswith("-"):
        multiplier = -1

    dec_f = dec_d + multiplier * ((dec_m / 60) + (dec_s / 3600))

    return round(dec_f, 6)


def bv_to_hex_color(bv_index):
    """
    Returns hex color for a BV Index

    List of BV colors from -0.40 -> 2.00 (with 0.05 increments)
    source: http://www.vendian.org/mncharity/dir3/starcolor/details.html
    """
    bv_colors = [
        "#9bb2ff",
        "#9eb5ff",
        "#a3b9ff",
        "#aabfff",
        "#b2c5ff",
        "#bbccff",
        "#c4d2ff",
        "#ccd8ff",
        "#d3ddff",
        "#dae2ff",
        "#dfe5ff",
        "#e4e9ff",
        "#e9ecff",
        "#eeefff",
        "#f3f2ff",
        "#f8f6ff",
        "#fef9ff",
        "#fff9fb",
        "#fff7f5",
        "#fff5ef",
        "#fff3ea",
        "#fff1e5",
        "#ffefe0",
        "#ffeddb",
        "#ffebd6",
        "#ffe9d2",
        "#ffe8ce",
        "#ffe6ca",
        "#ffe5c6",
        "#ffe3c3",
        "#ffe2bf",
        "#ffe0bb",
        "#ffdfb8",
        "#ffddb4",
        "#ffdbb0",
        "#ffdaad",
        "#ffd8a9",
        "#ffd6a5",
        "#ffd5a1",
        "#ffd29c",
        "#ffd096",
        "#ffcc8f",
        "#ffc885",
        "#ffc178",
        "#ffb765",
        "#ffa94b",
        "#ff9523",
        "#ff7b00",
        "#ff5200",
    ]
    color_index = round((bv_index + 0.4) / 0.05)

    if color_index < 0 or color_index > len(bv_colors) - 1:
        return None

    return bv_colors[color_index]


def azimuth_to_string(azimuth_degrees: int):
    if azimuth_degrees >= 360:
        azimuth_degrees -= 360
    direction_strings = ["N", "NE", "E", "SE", "S", "SW", "W", "NW", "N"]
    return direction_strings[int(azimuth_degrees / 40)]


def dt_or_now(dt):
    return dt or timezone("UTC").localize(datetime.now())


def points_on_line(start, end, num_points=100):
    """Generates points along a line segment.

    Args:
        start (tuple): (x, y) coordinates of the starting point.
        end (tuple): (x, y) coordinates of the ending point.
        num_points (int): Number of points to generate.

    Returns:
        list: List of (x, y) coordinates of the generated points.
    """

    x_coords = np.linspace(start[0], end[0], num_points)
    y_coords = np.linspace(start[1], end[1], num_points)

    return list(zip(x_coords, y_coords))
