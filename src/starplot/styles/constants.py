from enum import Enum


class GradientType(str, Enum):
    LINEAR = "linear"
    RADIAL = "radial"


class FontWeightEnum(int, Enum):
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


class FontStyleEnum(str, Enum):
    NORMAL = "normal"
    ITALIC = "italic"
    OBLIQUE = "oblique"


class MarkerSymbolEnum(str, Enum):
    """Options for marker symbols"""

    PLUS = "plus"
    """+"""

    CIRCLE = "circle"
    """\u25cf"""

    SQUARE = "square"
    """\u25a0"""

    STAR = "star"
    """\u2605"""

    DIAMOND = "diamond"
    """\u25c6"""

    TRIANGLE = "triangle"
    """\u23f6"""

    CIRCLE_CROSS = "circle_cross"
    """\u1aa0"""

    CIRCLE_CROSSHAIR = "circle_crosshair"
    """No preview available, but this is the standard symbol for planetary nebulae"""

    CIRCLE_LINE = "circle_line"
    """\u29b5  the standard symbol for double stars"""

    COMET = "comet"
    """\u2604"""

    STAR_4 = "star_4"
    """\u2726"""

    STAR_8 = "star_8"
    """\u2734"""

    ELLIPSE = "ellipse"
    """\u2b2d"""

    SATELLITE = "satellite"
    """\U0001f6f0 No preview available, but this is a satellite icon (solar panels + dish antenna)"""


class LineStyleEnum(str, Enum):
    SOLID = "solid"
    DASHED = "dashed"
    DASHED_DOTS = "dashdot"
    DOTTED = "dotted"

    def css(self) -> str | None:
        return {
            LineStyleEnum.SOLID: None,
            LineStyleEnum.DASHED: "12,6",
            LineStyleEnum.DOTTED: "0,5",
            LineStyleEnum.DASHED_DOTS: "10,2,10",
        }.get(self.value)

    def values(self) -> str | None:
        return {
            LineStyleEnum.SOLID: None,
            LineStyleEnum.DASHED: (12, 6),
            LineStyleEnum.DOTTED: (0, 5),
            LineStyleEnum.DASHED_DOTS: (10, 2, 10),
        }.get(self.value)


class CapStyleEnum(str, Enum):
    BUTT = "butt"
    SQUARE = "square"
    ROUND = "round"

    def css(self) -> str | None:
        return {
            CapStyleEnum.BUTT: "butt",
            CapStyleEnum.ROUND: "round",
            CapStyleEnum.SQUARE: "square",
        }.get(self.value)


class JoinStyleEnum(str, Enum):
    MITRE = "mitre"
    BEVEL = "bevel"
    ROUND = "round"


class LegendLocationEnum(str, Enum):
    """Options for the location of the map legend, relative to the axes"""

    INSIDE_TOP_LEFT = "inside top left"
    INSIDE_TOP_RIGHT = "inside top right"
    INSIDE_BOTTOM_RIGHT = "inside bottom right"
    INSIDE_BOTTOM_LEFT = "inside bottom left"

    OUTSIDE_TOP_LEFT = "outside top left"
    OUTSIDE_TOP_RIGHT = "outside top right"
    OUTSIDE_BOTTOM_RIGHT = "outside bottom right"
    OUTSIDE_BOTTOM_LEFT = "outside bottom left"


class AnchorPointEnum(str, Enum):
    """Options for the anchor point of labels"""

    CENTER = "center"
    LEFT_CENTER = "left center"
    RIGHT_CENTER = "right center"
    TOP_LEFT = "top left"
    TOP_RIGHT = "top right"
    TOP_CENTER = "top center"
    BOTTOM_LEFT = "bottom left"
    BOTTOM_RIGHT = "bottom right"
    BOTTOM_CENTER = "bottom center"

    @staticmethod
    def from_str(value: str) -> "AnchorPointEnum":
        options = {ap.value: ap for ap in AnchorPointEnum}
        return options.get(value)


class AlignmentEnum(str, Enum):
    """Alignment options for the legend's title and entries"""

    LEFT = "left"
    RIGHT = "right"
    CENTER = "center"


class ZOrderEnum(int, Enum):
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
