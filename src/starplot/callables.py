import math

from typing import Callable

from starplot.models import SimpleObject
from starplot.utils import bv_to_hex_color


def size_by_magnitude_factory(
    threshold: float, under_threshold_size: float
) -> Callable[[SimpleObject], float]:
    """
    Creates a new version of `size_by_magnitude` with a custom threshold

    Args:
        threshold: The threshold at which size will be a constant value. In other words, if an object's magnitude is more than or equal to this number, then its size will be the constant `under_threshold_size`
        under_threshold_size: Size for objects that have a magnitude greater than or equal to the treshold

    Returns:
        A callable for calculating size based on magnitude

    """

    def size_fn(obj: SimpleObject) -> float:
        m = obj.magnitude
        if m >= threshold:
            size = under_threshold_size
        else:
            size = 20 ** math.log(threshold - m)

        return size

    return size_fn


_size_by_magnitude_default = size_by_magnitude_factory(7.6, 2.36)


def size_by_magnitude(obj: SimpleObject) -> float:
    """
    Calculates size by logarithmic scale of magnitude:

    ```python
    if magnitude >= 7.6:
        size = 2.36
    else:
        size = 20 ** math.log(8 - magnitude)
    ```
    """
    return _size_by_magnitude_default(obj)


def size_by_magnitude_simple(obj):
    m = obj.magnitude
    if m < 1.6:
        return (9 - m) ** 2.85
    elif m < 4.6:
        return (8 - m) ** 2.92
    elif m < 5.8:
        return (9 - m) ** 2.46

    return 2.23

def size_by_magnitude_for_optic(obj):
    m = obj.magnitude

    if m < 4.6:
        return (9 - m) ** 3.76

    elif m < 5.85:
        return (9 - m) ** 3.72
    elif m < 9:
        return (13 - m) ** 1.91

    return 4.93


def alpha_by_magnitude(obj):
    """
    Basic calculator for alpha, based on magnitude:

    ```python
    if magnitude < 4.6:
        alpha = 1
    elif magnitude < 5.8:
        alpha = 0.9
    else:
        alpha = (16 - m) * 0.09
    ```
    """
    m = obj.magnitude
    if m < 4.6:
        return 1
    elif m < 5.8:
        return 0.9

    return (16 - m) * 0.09


def color_by_bv(obj) -> str:
    """
    Calculates color by the object's [B-V index](https://en.wikipedia.org/wiki/Color_index)

    Color hex values from: [Mitchell Charity](http://www.vendian.org/mncharity/dir3/starcolor/details.html)
    """
    if math.isnan(obj.bv):
        bv = 0
    else:
        bv = obj.bv
    return bv_to_hex_color(bv)
