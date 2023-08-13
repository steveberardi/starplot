import math

from matplotlib.transforms import Bbox


def bbox_minmax_angle(bbox: Bbox) -> float:
    """Calculate angle between min/max of bounding box"""
    x, y = (bbox.max[0] - bbox.min[0], bbox.max[1] - bbox.min[1])
    return math.degrees(math.atan2(y, x))


def in_circle(x, y, center_x=0, center_y=0, radius=0.9) -> bool:
    """Determine if a point (x,y) is inside a circle"""
    return (x - center_x) ** 2 + (y - center_y) ** 2 < (radius**2)
