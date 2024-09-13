from functools import cache

from matplotlib import transforms
from matplotlib.path import Path

import numpy as np


def ellipse_points(
    center_x, center_y, semi_major_axis, semi_minor_axis, num_points=100
):
    """Generates points on an ellipse.

    Args:
        center_x: X coordinate of the center.
        center_y: Y coordinate of the center.
        semi_major_axis: Length of the semi-major axis.
        semi_minor_axis: Length of the semi-minor axis.
        num_points: Number of points to generate.

    Returns:
        A list of (x, y) coordinates of the ellipse points.
    """

    theta = np.linspace(0, 2 * np.pi, num_points)
    x = center_x + semi_major_axis * np.cos(theta)
    y = center_y + semi_minor_axis * np.sin(theta)

    return list(zip(x, y))


@cache
def ellipse():
    verts = ellipse_points(0, 0, 1, 0.5)

    codes = [
        Path.MOVETO,
    ]
    codes.extend([Path.LINETO] * 98)
    codes.extend([Path.CLOSEPOLY])
    p = Path(verts, codes).transformed(transforms.Affine2D().rotate_deg(15))

    return p


@cache
def circle_cross():
    verts = ellipse_points(0, 0, 1, 1)

    codes = [
        Path.MOVETO,
    ]
    codes.extend([Path.LINETO] * 98)
    codes.extend([Path.CLOSEPOLY])

    verts.extend(
        [
            (-1, 0),
            (1, 0),
            (0, 1),
            (0, -1),
        ]
    )
    codes.extend(
        [
            Path.MOVETO,
            Path.LINETO,
            Path.MOVETO,
            Path.LINETO,
        ]
    )

    return Path(verts, codes)


@cache
def circle_line():
    verts = ellipse_points(0, 0, 1, 1)

    codes = [
        Path.MOVETO,
    ]
    codes.extend([Path.LINETO] * 98)
    codes.extend([Path.CLOSEPOLY])

    verts.extend(
        [
            (-1.9, 0),
            (1.9, 0),
            (-1.9, 0.04),
            (1.9, 0.04),
            (-1.9, -0.04),
            (1.9, -0.04),
        ]
    )
    codes.extend(
        [
            Path.MOVETO,
            Path.LINETO,
            Path.MOVETO,
            Path.LINETO,
            Path.MOVETO,
            Path.LINETO,
        ]
    )

    return Path(verts, codes)
