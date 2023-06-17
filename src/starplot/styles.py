from enum import Enum

from pydantic import BaseModel
from pydantic.color import Color


class FontWeightEnum(str, Enum):
    NORMAL = "normal"
    BOLD = "bold"
    HEAVY = "heavy"
    LIGHT = "light"
    ULTRA_BOLD = "ultrabold"
    ULTRA_LIGHT = "ultralight"


class FontStyleEnum(str, Enum):
    NORMAL = "normal"
    ITALIC = "italic"
    OBLIQUE = "oblique"


class MarkerSymbolEnum(str, Enum):
    POINT = "."
    CIRCLE = "o"
    SQUARE = "s"
    STAR = "*"
    DIAMOND = "D"
    TRIANGLE = "^"


class MarkerStyle(BaseModel):
    color: Color = Color("#000")
    symbol: MarkerSymbolEnum = MarkerSymbolEnum.POINT
    size: int = 4
    fillstyle: str = "none"
    visible: bool = True


class LabelStyle(BaseModel):
    font_size: int = 8
    font_weight: FontWeightEnum = FontWeightEnum.NORMAL
    font_color: Color = Color("#000")
    font_alpha: float = 1
    visible: bool = True


class ObjectStyle(BaseModel):
    marker: MarkerStyle = MarkerStyle()
    label: LabelStyle = LabelStyle()


class PlotStyle(BaseModel):
    """
    Base plotting style (monochrome)
    """

    # Base
    background_color: Color = Color("#fff")

    # Borders
    border_font_size: int = 18
    border_font_weight: FontWeightEnum = FontWeightEnum.BOLD
    border_font_color: Color = Color("#000")
    border_line_color: Color = Color("#000")
    border_bg_color = Color("#fff")

    # Stars
    star_color: Color = Color("#000")
    star_font_size: int = 9
    star_font_weight: FontWeightEnum = FontWeightEnum.BOLD
    star_font_color: Color = Color("#000")
    star_font_alpha: float = 1

    # Constellations
    constellation_font_size: int = 7
    constellation_font_weight: FontWeightEnum = FontWeightEnum.LIGHT
    constellation_font_color: Color = Color("#000")
    constellation_line_width: int = 1
    constellation_line_color: Color = Color("#c8c8c8")
    constellation_line_alpha: float = 1.0


MONO = PlotStyle()

BLUE = PlotStyle(
    background_color="#f1f6ff",
    # Borders
    border_font_color="#f1f6ff",
    border_line_color="#2f4358",
    border_bg_color="#7997b9",
    # Stars
    # starname_font_weight = "bold"
    # Constellations
    constellation_line_width=2,
    constellation_line_color=Color("#6ba832"),
    constellation_line_alpha=0.2,
)

RED = PlotStyle(
    background_color="#ffd0d0",
    # Borders
    border_font_color="#7a0000",
    border_line_color="#7a0000",
    border_bg_color="#ff8e8e",
    # Stars
    star_color="#7a0000",
    star_font_color="#7a0000",
    # Constellations
    constellation_font_color="#7a0000",
    constellation_line_width=2,
    constellation_line_color=Color("#ff8e8e"),
    constellation_line_alpha=0.2,
)

CHALK = PlotStyle(
    background_color="#4c566a",
    # Borders
    border_font_color="#a3be8c",
    border_line_color="#a3be8c",
    border_bg_color="#2e3440",
    # Stars
    star_color="#88c0d0",
    star_font_color="#88c0d0",
    # Constellations
    # constellation_font_color="rgb(168, 189, 145)",
    constellation_font_color="rgb(230, 204, 147)",  # yellow
    constellation_line_width=1,
    constellation_line_color="rgb(230, 204, 147)",
    constellation_line_alpha=0.36,
)
