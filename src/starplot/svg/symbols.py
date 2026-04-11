import math

from starplot.styles import MarkerSymbolEnum
from starplot.svg.elements import Circle, Line, Ellipse, Group, Rectangle, Polygon

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
    r = round(size / 4, 4)
    n = round(2 * r, 4)

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


def circle_line(x, y, size, attrs):
    r = round(size / 2, 4)
    n = round(1.8 * r, 4)
    return Group(
        attrs=attrs,
        children=[
            Circle(cx=x, cy=y, r=r),
            Line(
                x1=x - n,
                y1=y,
                x2=x + n,
                y2=y,
                attrs={"stroke-width": (attrs.get("stroke-width") or 2) * 2},
            ),
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


def square(x, y, size, attrs):
    r = size / 2
    return Rectangle(
        x=x - r,
        y=y - r,
        height=size,
        width=size,
        attrs=attrs,
    )


def triangle(
    x: float,
    y: float,
    size: float,
    attrs: dict,
):
    r = size / math.sqrt(3)
    points = []
    for i in range(3):
        angle = math.radians(-90 + i * 120)
        xx = round(x + r * math.cos(angle), 4)
        yy = round(y + r * math.sin(angle), 4)
        points.append((xx, yy))

    return Polygon(points=points, attrs=attrs)


def diamond(
    x: float,
    y: float,
    size: float,
    attrs: dict,
):
    """
    Returns 4 (x, y) points of a diamond centered at (cx, cy).
    """
    points = [
        (x, y - size / 2),  # top
        (x + size / 2, y),  # right
        (x, y + size / 2),  # bottom
        (x - size / 2, y),  # left
    ]
    return Polygon(points=points, attrs=attrs)


def star_4(
    x: float,
    y: float,
    size: float,
    attrs: dict,
):
    points = []
    for i in range(8):
        angle = math.radians(-90 + i * 45)
        r = size / 2 if i % 2 == 0 else size / 5
        points.append(
            (
                x + r * math.cos(angle),
                y + r * math.sin(angle),
            )
        )
    return Polygon(points=points, attrs=attrs)


def plus(x: float, y: float, size: float, attrs: dict):
    t = 6
    s = size / 2
    points = [
        (x - t, y - s),  # top-left of top arm
        (x + t, y - s),  # top-right of top arm
        (x + t, y - t),  # inner top-right
        (x + s, y - t),  # right arm top
        (x + s, y + t),  # right arm bottom
        (x + t, y + t),  # inner bottom-right
        (x + t, y + s),  # bottom arm right
        (x - t, y + s),  # bottom arm left
        (x - t, y + t),  # inner bottom-left
        (x - s, y + t),  # left arm bottom
        (x - s, y - t),  # left arm top
        (x - t, y - t),  # inner top-left
    ]
    return Polygon(points=points, attrs=attrs)


def comet(cx: float, cy: float, size: float, attrs: dict, steps: int = 100):
    head_r = size * 0.172
    tail_len = size * 0.7
    tail_angle = math.radians(45)

    tip = (
        cx + math.cos(tail_angle) * tail_len,
        cy - math.sin(tail_angle) * tail_len,
    )

    # Where the tail edges meet the head circle (±90° from tail axis)
    a_upper = tail_angle + math.radians(90)  # 135°
    a_lower = tail_angle - math.radians(90)  # 315°

    def on_circle(angle):
        return (cx + math.cos(angle) * head_r, cy - math.sin(angle) * head_r)

    end = a_lower
    if end <= a_upper:
        end += math.pi * 2

    arc = [on_circle(a_upper + (end - a_upper) * i / steps) for i in range(steps + 1)]

    points = [tip, on_circle(a_upper)] + arc + [on_circle(a_lower), tip]
    return Polygon(points=points, attrs=attrs)


SYMBOL_FUNCTIONS = {
    MarkerSymbolEnum.POINT: circle,
    MarkerSymbolEnum.CIRCLE: circle,
    MarkerSymbolEnum.CIRCLE_CROSS: circle_cross,
    MarkerSymbolEnum.CIRCLE_CROSSHAIR: circle_crosshair,
    MarkerSymbolEnum.CIRCLE_LINE: circle_line,
    MarkerSymbolEnum.ELLIPSE: ellipse,
    MarkerSymbolEnum.SQUARE: square,
    MarkerSymbolEnum.TRIANGLE: triangle,
    MarkerSymbolEnum.DIAMOND: diamond,
    MarkerSymbolEnum.STAR_4: star_4,
    MarkerSymbolEnum.PLUS: plus,
    MarkerSymbolEnum.COMET: comet,
}


def create(x, y, size, symbol: MarkerSymbolEnum, attrs: dict):
    attrs = attrs or {}
    return SYMBOL_FUNCTIONS.get(symbol)(x, y, size, attrs)
