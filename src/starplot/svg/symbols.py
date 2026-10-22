import math

from starplot.settings import settings
from starplot.styles.types import MarkerSymbol
from starplot.svg.elements import Circle, Ellipse, Group, Line, Polygon, Rectangle

"""
(0,0)          (100,0)
  ┌──────────────┐
  │              │
  │   (50,50)    │
  │              │
  └──────────────┘
(0,100)        (100,100)

Sizing:

Most symbols are sized so that they fit inside a square with sides equal to `size`.

The circle-based symbols that have extra parts outside of the circle (`circle_line`,
`circle_crosshair`, and `circle_double_border`) are the exception: their `size` is the
diameter of their circle, so that the circle is the same as a plain `circle` marker of
the same size. Use `extent()` to get the full width and height of a symbol.
"""

# half-length of the line in `circle_line`, relative to the radius of its circle
CIRCLE_LINE_EXTENT = 1.8

# outer ring radius of `circle_double_border`, relative to the radius of its center circle
CIRCLE_DOUBLE_BORDER_EXTENT = 1.7038


def circle_cross(x, y, size, attrs):
    r = round(size / 2, settings.precision)
    return Group(
        attrs=attrs,
        children=[
            Circle(cx=x, cy=y, r=r),
            Line(x1=x - r, y1=y, x2=x + r, y2=y),
            Line(x1=x, y1=y + r, x2=x, y2=y - r),
        ],
    )


def circle_crosshair(x, y, size, attrs):
    r = round(size / 2, settings.precision)
    n = round(2 * r, settings.precision)

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
    r = round(size / 2, settings.precision)
    n = round(CIRCLE_LINE_EXTENT * r, settings.precision)
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
    r = round(size / 2, settings.precision)
    return Circle(cx=x, cy=y, r=r, attrs=attrs)


def ellipse(x, y, size, attrs):
    angle = math.radians(20)
    aspect = 0.6
    # scaled so the rotated ellipse's horizontal extent is exactly the box width
    rx = size / 2 / math.sqrt(math.cos(angle) ** 2 + (aspect * math.sin(angle)) ** 2)
    rx = round(rx, settings.precision)
    ry = round(rx * aspect, settings.precision)
    _attrs = {
        "transform": f"rotate(-20, {x}, {y})",
        **attrs,
    }
    return Ellipse(cx=x, cy=y, rx=rx, ry=ry, attrs=_attrs)


def square(x, y, size, attrs):
    r = size / 2
    return Rectangle(
        x=round(x - r, settings.precision),
        y=round(y - r, settings.precision),
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
    # the shape spans from -r to r/2 around its circumcenter, so shift it to center its bounding box
    y = y + r / 4
    points = []
    for i in range(3):
        angle = math.radians(-90 + i * 120)
        xx = round(x + r * math.cos(angle), settings.precision)
        yy = round(y + r * math.sin(angle), settings.precision)
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


def create_star_function(num_points: int):
    """Returns a function to create a star with specified number of points"""

    def _star(
        x: float,
        y: float,
        size: float,
        attrs: dict,
    ):
        points = []
        for i in range(num_points * 2):
            angle = math.radians(-90 + i * (180 / num_points))
            r = size / 2 if i % 2 == 0 else size / 5
            points.append(
                (
                    round(x + r * math.cos(angle), settings.precision),
                    round(y + r * math.sin(angle), settings.precision),
                )
            )
        return Polygon(points=points, attrs=attrs)

    return _star


def plus(x: float, y: float, size: float, attrs: dict):
    t = size / 8  # thickness
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
    tail_angle = math.radians(45)

    # Head radius and tail length keep the original comet proportions. The bounding
    # box of the head + tail is a square (the tail is at 45 degrees), so it's scaled
    # uniformly to fill the size box, then shifted so the box is centered on (cx, cy).
    head_r = 0.172
    tail_len = 0.7
    extent = head_r + tail_len * math.cos(tail_angle)
    scale = size / extent
    head_r *= scale
    tail_len *= scale

    offset = (extent * scale) / 2 - head_r
    cx -= offset
    cy += offset

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


def satellite(x: float, y: float, size: float, attrs: dict):
    # scaled so the rotated panel corners touch the box edges
    size = size * math.sqrt(2) / 2 / 0.64
    panel_w = size * 0.36
    panel_h = size * 0.24
    gap = size * 0.05
    body_w = size * 0.22
    body_h = size * 0.20

    panel_y0 = round(y - panel_h / 2, settings.precision)
    left_x0 = round(x - body_w / 2 - gap - panel_w, settings.precision)
    right_x0 = round(x + body_w / 2 + gap, settings.precision)

    elements = [
        Rectangle(
            x=left_x0,
            y=panel_y0,
            width=round(panel_w, settings.precision),
            height=round(panel_h, settings.precision),
        ),
        Rectangle(
            x=right_x0,
            y=panel_y0,
            width=round(panel_w, settings.precision),
            height=round(panel_h, settings.precision),
        ),
        Rectangle(
            x=round(x - body_w / 2, settings.precision),
            y=round(y - body_h / 2, settings.precision),
            width=round(body_w, settings.precision),
            height=round(body_h, settings.precision),
        ),
    ]

    mid_y = round(y, settings.precision)

    # grid lines on each solar panel (3 columns x 2 rows)
    for panel_x0 in (left_x0, right_x0):
        col_step = panel_w / 3
        for i in (1, 2):
            cx = round(panel_x0 + col_step * i, settings.precision)
            elements.append(
                Line(
                    x1=cx,
                    y1=panel_y0,
                    x2=cx,
                    y2=round(panel_y0 + panel_h, settings.precision),
                )
            )
        elements.append(
            Line(
                x1=panel_x0,
                y1=mid_y,
                x2=round(panel_x0 + panel_w, settings.precision),
                y2=mid_y,
            )
        )

    # connect each panel to the body with a single line through the center
    elements.append(
        Line(
            x1=round(left_x0 + panel_w, settings.precision),
            y1=mid_y,
            x2=round(x - body_w / 2, settings.precision),
            y2=mid_y,
        )
    )
    elements.append(
        Line(
            x1=round(x + body_w / 2, settings.precision),
            y1=mid_y,
            x2=right_x0,
            y2=mid_y,
        )
    )

    return Group(
        attrs={**attrs, "transform": f"rotate(-45, {x}, {y})"},
        children=elements,
    )


def circle_double_border(x: float, y: float, size: float, attrs: dict):
    # `size` is the diameter of the solid center circle; the rings are outside of it
    def ring(radius: float):
        return Circle(
            cx=x,
            cy=y,
            r=round(radius, settings.precision),
            attrs={"fill": "none"},
        )

    return Group(
        attrs=attrs,
        children=[
            # the filled center is always solid, even if the border is dashed
            Circle(
                cx=x,
                cy=y,
                r=round(size / 2, settings.precision),
                attrs={"stroke-dasharray": "none"},
            ),
            ring(size * 0.6944),
            ring(size * 0.8519),
        ],
    )


SYMBOL_FUNCTIONS = {
    "circle": circle,
    "circle_cross": circle_cross,
    "circle_crosshair": circle_crosshair,
    "circle_line": circle_line,
    "circle_double_border": circle_double_border,
    "ellipse": ellipse,
    "square": square,
    "triangle": triangle,
    "diamond": diamond,
    "star": create_star_function(num_points=5),
    "star_4": create_star_function(num_points=4),
    "star_8": create_star_function(num_points=8),
    "plus": plus,
    "comet": comet,
    "satellite": satellite,
}


def extent(symbol: MarkerSymbol, size: float) -> tuple[float, float]:
    """Returns the full (width, height) of a symbol drawn at the given size"""
    if symbol == "circle_line":
        return size * CIRCLE_LINE_EXTENT, size
    if symbol == "circle_crosshair":
        return size * 2, size * 2
    if symbol == "circle_double_border":
        return size * CIRCLE_DOUBLE_BORDER_EXTENT, size * CIRCLE_DOUBLE_BORDER_EXTENT
    return size, size


def create(x, y, size, symbol: MarkerSymbol, attrs: dict):
    attrs = attrs or {}
    return SYMBOL_FUNCTIONS.get(symbol)(x, y, size, attrs)
