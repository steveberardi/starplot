from enum import Enum

from pydantic import BaseModel
from pydantic.color import Color


class FillStyleEnum(str, Enum):
    FULL = "full"
    LEFT = "left"
    RIGHT = "right"
    BOTTOM = "bottom"
    TOP = "top"
    NONE = "none"


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
    fill: FillStyleEnum = FillStyleEnum.NONE
    alpha: float = 1.0
    visible: bool = True

    @property
    def matplot_kwargs(self) -> dict:
        return dict(
            color=self.color.as_hex(),
            marker=self.symbol,
            markersize=self.size,
            fillstyle=self.fill,
            alpha=self.alpha,
        )


class LineStyle(BaseModel):
    width: int = 1
    color: Color = Color("#000")
    alpha: float = 1.0
    zorder: int = -1

    @property
    def matplot_kwargs(self) -> dict:
        return dict(
            colors=self.color.as_hex(),
            linewidths=self.width,
            alpha=self.alpha,
            zorder=self.zorder,
        )


class LabelStyle(BaseModel):
    font_size: int = 8
    font_weight: FontWeightEnum = FontWeightEnum.NORMAL
    font_color: Color = Color("#000")
    font_alpha: float = 1
    font_style: FontStyleEnum = FontStyleEnum.NORMAL
    zorder: int = 1
    visible: bool = True

    @property
    def matplot_kwargs(self) -> dict:
        return dict(
            color=self.font_color.as_hex(),
            fontsize=self.font_size,
            fontstyle=self.font_style,
            weight=self.font_weight,
            alpha=self.font_alpha,
            zorder=self.zorder,
        )


class ObjectStyle(BaseModel):
    marker: MarkerStyle = MarkerStyle()
    label: LabelStyle = LabelStyle()


class PathStyle(BaseModel):
    line: LineStyle = LineStyle()
    label: LabelStyle = LabelStyle()


class PlotStyle(BaseModel):
    """
    Base plotting style (grayscale)
    """

    # Base
    background_color: Color = Color("#fff")
    text_border_width: int = 2
    text_offset_x: float = 0.005
    text_offset_y: float = 0.005

    # Borders
    border_font_size: int = 18
    border_font_weight: FontWeightEnum = FontWeightEnum.BOLD
    border_font_color: Color = Color("#000")
    border_line_color: Color = Color("#000")
    border_bg_color = Color("#fff")

    # Stars
    star: ObjectStyle = ObjectStyle(
        marker=MarkerStyle(fillstyle=FillStyleEnum.FULL),
        label=LabelStyle(font_size=9, font_weight=FontWeightEnum.BOLD),
    )

    # Deep Sky Objects (DSOs)
    dso: ObjectStyle = ObjectStyle(
        marker=MarkerStyle(
            symbol=MarkerSymbolEnum.TRIANGLE, size=4, fillstyle=FillStyleEnum.FULL
        ),
        label=LabelStyle(font_size=8),
    )

    # Constellations
    constellation: PathStyle = PathStyle(
        line=LineStyle(color="#c8c8c8"),
        label=LabelStyle(font_size=7, font_weight=FontWeightEnum.LIGHT),
    )


GRAYSCALE = PlotStyle()

BLUE = PlotStyle(
    background_color="#f1f6ff",
    # Borders
    border_font_color="#f1f6ff",
    border_line_color="#2f4358",
    border_bg_color="#7997b9",
    # Constellations
    constellation=PathStyle(
        line=LineStyle(width=2, color="#6ba832", alpha=0.2),
        label=LabelStyle(font_size=7, font_weight=FontWeightEnum.LIGHT),
    ),
)

RED = PlotStyle(
    background_color="#ffd0d0",
    # Borders
    border_font_color="#7a0000",
    border_line_color="#7a0000",
    border_bg_color="#ff8e8e",
    # Stars
    star=ObjectStyle(
        marker=MarkerStyle(color="#7a0000"),
        label=LabelStyle(font_color="#7a0000"),
    ),
    # DSOs
    dso=ObjectStyle(
        marker=MarkerStyle(
            color="#7a0000",
            symbol=MarkerSymbolEnum.SQUARE,
            size=4,
            fill=FillStyleEnum.FULL,
        ),
        label=LabelStyle(font_color="#7a0000"),
    ),
    # Constellations
    constellation=PathStyle(
        line=LineStyle(width=2, color="#ff8e8e", alpha=0.2),
        label=LabelStyle(
            font_size=7, font_weight=FontWeightEnum.LIGHT, font_color="#7a0000"
        ),
    ),
)

CHALK = PlotStyle(
    background_color="#4c566a",
    # Borders
    border_font_color="#a3be8c",
    border_line_color="#a3be8c",
    border_bg_color="#2e3440",
    # Stars
    star=ObjectStyle(
        marker=MarkerStyle(color="#88c0d0"),
        label=LabelStyle(
            font_size=9, font_color="#88c0d0", font_weight=FontWeightEnum.BOLD
        ),
    ),
    # DSOs
    dso=ObjectStyle(
        marker=MarkerStyle(
            color="rgb(230, 204, 147)",
            symbol=MarkerSymbolEnum.TRIANGLE,
            size=4,
            fill=FillStyleEnum.FULL,
            alpha=0.46,
        ),
        label=LabelStyle(
            font_size=7,
            font_color="rgb(230, 204, 147)",
            font_weight=FontWeightEnum.LIGHT,
            font_alpha=0.6,
        ),
    ),
    # Constellations
    constellation=PathStyle(
        line=LineStyle(width=1, color="rgb(230, 204, 147)", alpha=0.36),
        label=LabelStyle(
            font_size=7,
            font_weight=FontWeightEnum.LIGHT,
            font_color="rgb(230, 204, 147)",
            font_alpha=0.6,
        ),
    ),
)
