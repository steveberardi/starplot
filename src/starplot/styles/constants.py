from enum import Enum


class GradientType(str, Enum):
    LINEAR = "linear"
    RADIAL = "radial"


class FontWeight:
    """Options for font weight."""

    THIN = 100
    EXTRA_LIGHT = 200
    LIGHT = 300
    NORMAL = 400
    MEDIUM = 500
    SEMI_BOLD = 600
    BOLD = 700
    EXTRA_BOLD = 800
    HEAVY = 900


class FontStyle:
    NORMAL = "normal"
    ITALIC = "italic"
    OBLIQUE = "oblique"


class DashArray:
    """Options for a line's dash style"""

    SOLID = "solid"
    DASHED = "dashed"
    DASHED_DOTS = "dashdot"
    DOTTED = "dotted"


class CapStyle:
    BUTT = "butt"
    SQUARE = "square"
    ROUND = "round"


class JoinStyle:
    MITRE = "mitre"
    BEVEL = "bevel"
    ROUND = "round"


class LegendLocation:
    """Options for the location of the map legend, relative to the axes"""

    INSIDE_TOP_LEFT = "inside_top_left"
    INSIDE_TOP_RIGHT = "inside_top_right"
    INSIDE_BOTTOM_RIGHT = "inside_bottom_right"
    INSIDE_BOTTOM_LEFT = "inside_bottom_left"

    OUTSIDE_TOP_LEFT = "outside_top_left"
    OUTSIDE_TOP_RIGHT = "outside_top_right"
    OUTSIDE_BOTTOM_RIGHT = "outside_bottom_right"
    OUTSIDE_BOTTOM_LEFT = "outside_bottom_left"


class AnchorPoint:
    """Options for the anchor point of labels"""

    CENTER = "center"
    LEFT_CENTER = "left_center"
    RIGHT_CENTER = "right_center"
    TOP_LEFT = "top_left"
    TOP_RIGHT = "top_right"
    TOP_CENTER = "top_center"
    BOTTOM_LEFT = "bottom_left"
    BOTTOM_RIGHT = "bottom_right"
    BOTTOM_CENTER = "bottom_center"


class HorizontalAlignment:
    """Horizontal alignment options for the legend's title and entries"""

    LEFT = "left"
    RIGHT = "right"
    CENTER = "center"


class ZOrder:
    """
    Z Order presets for managing layers
    """

    LAYER_1 = -2_000
    """Bottom layer"""

    LAYER_2 = -1_000

    LAYER_3 = 0
    """Middle layer"""

    LAYER_4 = 1_000

    LAYER_5 = 2_000
    """Top layer"""
