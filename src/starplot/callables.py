import math
from collections.abc import Callable

from starplot.data.translations import translate
from starplot.models import Star
from starplot.styles import GradientStyle
from starplot.utils import bv_to_hex_color, hex_to_rgb, lighten_hex_color


def size_by_magnitude_factory(
    threshold: float,
    over_threshold_size: float,
    base: float = 20,
) -> Callable[[Star], float]:
    """
    Creates a new version of `size_by_magnitude_log` with a custom threshold and base multiplier:

    ```python
    if magnitude >= threshold:
        size = over_threshold_size
    else:
        size = base ** math.log(threshold - magnitude)
    ```

    Args:
        threshold: The threshold at which size will be a constant value. In other words, if an object's magnitude is more than or equal to this number, then its size will be the constant `under_threshold_size`
        over_threshold_size: Size for objects that have a magnitude greater than or equal to the treshold
        base: Base for objects that have a magnitude less than the threshold

    Returns:
        A callable for calculating size based on magnitude

    """

    def size_fn(star: Star) -> float:
        m = star.magnitude
        if m >= threshold:
            size = over_threshold_size
        else:
            size = base ** math.log(threshold - m)

        return size * 9

    return size_fn


def size_by_magnitude(star: Star) -> float:
    """
    Simple sizing by magnitude, using a step size of 1.

    ```python
    if mag <= 0:
        size = 3800
    elif mag <= 1:  # 0..1
        size = 2400
    elif mag <= 2:  # 1..2
        size = 1600
    elif mag <= 3:  # 2..3
        size = 1000
    elif mag <= 4:  # 3..4
        size = 600
    elif mag <= 5:  # 4..5
        size = 300
    elif mag <= 6:  # 5..6
        size = 120
    elif mag <= 7:  # 6..7
        size = 60
    elif mag <= 8:  # 7..8
        size = 40
    else:           # > 8
        size = 20

    ```
    """
    mag = star.magnitude
    size = 0
    if mag <= 1 or mag <= 2:  # 0..1
        size = 40
    elif mag <= 3:  # 2..3
        size = 30
    elif mag <= 4:  # 3..4
        size = 20
    elif mag <= 5:  # 4..5
        size = 15
    elif mag <= 6:  # 5..6
        size = 10
    elif mag <= 7:  # 6..7
        size = 6
    elif mag <= 8:  # 7..8
        size = 3
    else:  # > 8
        size = 2

    return size


def size_by_fov_factory(fov: float) -> Callable[[Star], float]:
    """
    Returns a callable for sizing stars based on the field of view of an optic.

    _This is the default star sizing function for OpticPlot._

    Args:
        fov: Field of view (in degrees)
    """
    fov_multiplier = 20 / fov

    return lambda s: size_by_magnitude(s) * fov_multiplier * 0.5


def size_by_magnitude_galaxy(star: Star) -> float:
    sizes = [
        15,
        15,
        10,
        8,
        5,
        3,
        2,
        1,
    ]
    mag = max(0, star.magnitude)
    mag_index = min(int(mag), len(sizes) - 1)
    return sizes[mag_index]


def opacity_by_magnitude(star: Star) -> float:
    """
    Basic calculator for opacity, based on magnitude:

    ```python
    if magnitude < 4.6:
        opacity = 1
    elif magnitude < 5.8:
        opacity = 0.9
    else:
        opacity = (16 - m) * 0.09
    ```
    """
    m = star.magnitude
    if m < 4.6:
        return 1
    elif m < 5.8:
        return 0.9

    return (16 - m) * 0.09


def color_by_bv(star: Star) -> str:
    """
    Calculates color by the object's [B-V index](https://en.wikipedia.org/wiki/Color_index)

    Color hex values from: [Mitchell Charity](http://www.vendian.org/mncharity/dir3/starcolor/details.html)
    """
    if math.isnan(star.bv):
        bv = 0
    else:
        bv = star.bv
    return bv_to_hex_color(bv)


def color_by_bv_gradient(star: Star) -> GradientStyle:
    """
    Calculates a radial gradient by the object's [B-V index](https://en.wikipedia.org/wiki/Color_index),
    meant to resemble how a star looks through binoculars or a telescope: a bright core that gradually fades to fully transparent at the edge.

    Uses the same base color as `color_by_bv`, lightened at the center of the gradient and faded to transparent at the outer edge.
    """
    color = color_by_bv(star) or "#ffffff"
    r, g, b = hex_to_rgb(color)

    return GradientStyle(
        stops=(
            (0.0, f"rgba({r}, {g}, {b}, 0)"),
            (0.6, color),
            (1.0, lighten_hex_color(color, 0.2)),
        ),
        type="radial",
    )


def floor_hours_label(value: float) -> str:
    """
    Returns the floor of the value, with an 'h' appended to it.

    Example: `floor_hours_label(50) = '3h'`

    Args:
        value: The value to label

    """
    return f"{math.floor(value / 15)}h"


def rounded_degrees_label(value: float) -> str:
    """
    Returns the rounded value with a degree symbol appended to it.

    Example: `rounded_degrees_label(50.45) = '50°'`

    Args:
        value: The value to label

    """
    return f"{round(value)}° "


def azimuth_with_cardinal_direction_label_factory(
    language: str,
) -> Callable[[float], str]:
    """
    Returns a callable for labeling azimuth values. The callable returns the cardinal directions
    (e.g. North, South, etc) where applicable, and returns the rounded azimuth value with a degree
    symbol appended for other azimuths (e.g. `'120°'`).

    _This is the default label function for azimuths on HorizonPlot._

    Args:
        language: Language for the cardinal directions
    """

    def az_label_fn(az):
        cardinal_directions = {
            0: "NORTH",
            90: "EAST",
            180: "SOUTH",
            270: "WEST",
        }
        label = translate(cardinal_directions.get(az), language)
        return label.upper() if label else f"{round(az)}\u00b0"

    return az_label_fn
