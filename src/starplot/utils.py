import math

from matplotlib.transforms import Bbox


def bbox_minmax_angle(bbox: Bbox) -> float:
    """Calculate angle between min/max of bounding box"""
    x, y = (bbox.max[0] - bbox.min[0], bbox.max[1] - bbox.min[1])
    return math.degrees(math.atan2(y, x))


def in_circle(x, y, center_x=0, center_y=0, radius=0.9) -> bool:
    """Determine if a point (x,y) is inside a circle"""
    return (x - center_x) ** 2 + (y - center_y) ** 2 < (radius**2)


def lon_to_ra(lon: float) -> (int, int, int):
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
