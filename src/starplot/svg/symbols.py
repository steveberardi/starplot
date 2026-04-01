from starplot.styles import MarkerSymbolEnum
from starplot.svg.elements import Circle, Line, Ellipse, Group

"""
(0,0)          (100,0)
  ┌──────────────┐
  │              │
  │   (50,50)    │
  │              │
  └──────────────┘
(0,100)        (100,100)
"""


def circle_cross(x, y, size, attrs):
    r = round(size / 2, 4)
    return Group(
        attrs=attrs,
        children=[
            Circle(cx=x, cy=y, r=r),
            Line(x1=x - r, y1=y, x2=x + r, y2=y),
            Line(x1=x, y1=y + r, x2=x, y2=y - r),
        ],
    )


def circle_crosshair(x, y, size, attrs):
    r = round(size / 2, 4)
    n = round(1.75 * r, 4)

    return Group(
        attrs=attrs,
        children=[
            Circle(cx=x, cy=y, r=r),
            Line(x1=x, y1=y - r, x2=x, y2=y - n),
            Line(x1=x + r, y1=y, x2=x + n, y2=y),
            Line(x1=x, y1=y + r, x2=x, y2=y + n),
            Line(x1=x - r, y1=y, x2=x - n, y2=y),
        ],
    )


def circle(x, y, size, attrs):
    r = round(size / 2, 4)
    return Circle(cx=x, cy=y, r=r, attrs=attrs)


def ellipse(x, y, size, attrs):
    rx = round(size * 0.5, 4)
    ry = round(size * 0.3, 4)
    _attrs = {
        "transform": f"rotate(-20, {x}, {y})",
        **attrs,
    }
    return Ellipse(cx=x, cy=y, rx=rx, ry=ry, attrs=_attrs)


SYMBOL_FUNCTIONS = {
    MarkerSymbolEnum.POINT: circle,
    MarkerSymbolEnum.CIRCLE: circle,
    MarkerSymbolEnum.CIRCLE_CROSS: circle_cross,
    MarkerSymbolEnum.CIRCLE_CROSSHAIR: circle_crosshair,
    MarkerSymbolEnum.ELLIPSE: ellipse,
}


def create(x, y, size, symbol: MarkerSymbolEnum, attrs: dict):
    attrs = attrs or {}
    return SYMBOL_FUNCTIONS.get(symbol)(x, y, size, attrs)
