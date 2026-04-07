from dataclasses import dataclass, field
from typing import ClassVar

from fontTools.pens.svgPathPen import SVGPathPen

from starplot.svg.fonts import find_font


@dataclass(slots=True, kw_only=True)
class Element:
    name: ClassVar[str] = "none"
    props: ClassVar[tuple[str]] = ()

    id: str | None = None

    attrs: dict = field(default_factory=dict)
    children: list["Element"] = field(default_factory=list)

    def render(self, indent: int = 0, text_as_path: bool = False) -> str:
        return render(self, indent, text_as_path)


@dataclass(slots=True, kw_only=True)
class SVG(Element):
    name: ClassVar[str] = "svg"
    props = ("xmlns", "x", "y", "height", "width")

    xmlns: str = "http://www.w3.org/2000/svg"
    x: float | None = None
    y: float | None = None
    height: float
    width: float

    def __post_init__(self):
        if not self.attrs.get("viewBox"):
            self.attrs["viewBox"] = f"0 0 {self.width} {self.height}"


@dataclass(slots=True, kw_only=True)
class Group(Element):
    name: ClassVar[str] = "g"


@dataclass(slots=True, kw_only=True)
class Defs(Element):
    name: ClassVar[str] = "defs"


@dataclass(slots=True, kw_only=True)
class ClipPath(Element):
    name: ClassVar[str] = "clipPath"


@dataclass(slots=True, kw_only=True)
class Circle(Element):
    name = "circle"
    props = ("cx", "cy", "r")

    cx: float
    cy: float
    r: float


@dataclass(slots=True, kw_only=True)
class Rectangle(Element):
    name = "rect"
    props = ("x", "y", "height", "width")

    x: float
    y: float
    height: float
    width: float


@dataclass(slots=True, kw_only=True)
class Polygon(Element):
    name = "polygon"
    props = ("points",)

    points: list[tuple[float, float]] = field(default_factory=list)

    def render_points(self):
        return " ".join([f"{x},{y}" for x, y in self.points])


@dataclass(slots=True, kw_only=True)
class Polyline(Element):
    name = "polyline"
    props = ("points",)

    points: list[tuple[float, float]] = field(default_factory=list)

    def render_points(self):
        return " ".join([f"{x},{y}" for x, y in self.points])


@dataclass(slots=True, kw_only=True)
class Line(Element):
    name = "line"
    props = ("x1", "y1", "x2", "y2")

    x1: float
    y1: float
    x2: float
    y2: float


@dataclass(slots=True, kw_only=True)
class Ellipse(Element):
    name = "ellipse"
    props = ("cx", "cy", "rx", "ry")

    cx: float
    cy: float
    rx: float
    ry: float


@dataclass(slots=True, kw_only=True)
class Path(Element):
    name = "path"
    props = ("d",)

    d: str


@dataclass(slots=True, kw_only=True)
class Text(Element):
    name = "text"
    props = ("x", "y")

    x: float
    y: float
    text: str

    def render_as_path(self):
        """

        TODO:
            - anchor points
        """
        font_family = self.attrs["font-family"].split(",")[0]
        font_weight = int(self.attrs["font-weight"])
        is_italic = self.attrs["font-style"] == "italic"
        font = find_font(family=font_family, weight=font_weight, italic=is_italic)

        x, y = self.x, self.y
        font_size = int(self.attrs["font-size"])
        glyf = font.getGlyphSet()
        cmap = font.getBestCmap()
        hmtx = font["hmtx"].metrics
        units_per_em = font["head"].unitsPerEm
        scale = font_size / units_per_em

        # Calculate total width first
        total_width = (
            sum(hmtx[cmap[ord(c)]][0] for c in self.text if ord(c) in cmap) * scale
        )

        anchor = self.attrs.get("text-anchor")
        if anchor == "end":
            x -= total_width
        elif anchor == "middle":
            x -= total_width / 2

        paths = []
        cursor_x = x
        line_height = font_size * 1.13

        for char in self.text:
            if char == "\n":
                cursor_x = x
                y += line_height
                continue

            codepoint = ord(char)
            glyph_name = cmap.get(codepoint)
            if not glyph_name:
                continue

            glyph = glyf[glyph_name]
            pen = SVGPathPen(glyf)
            glyph.draw(pen)

            pen_commands = pen.getCommands()

            if pen_commands:
                # SVG y-axis is flipped vs font coordinates
                paths.append(
                    Path(
                        attrs={
                            "transform": f"translate({cursor_x},{y}) scale({scale},{-scale})"
                        },
                        d=pen_commands,
                    )
                )

            cursor_x += hmtx[glyph_name][0] * scale

        group_attrs = {
            "fill": self.attrs.get("fill") or "#000",
            "fill-opacity": self.attrs.get("fill-opacity") or "1.0",
        }

        if self.attrs.get("stroke"):
            group_attrs["stroke"] = self.attrs.get("stroke")
            group_attrs["stroke-width"] = self.attrs.get("stroke-width")
            group_attrs["stroke-opacity"] = self.attrs.get("stroke-opacity")
            group_attrs["paint-order"] = "stroke fill"

        g = Group(id=self.id, children=paths, attrs=group_attrs)

        return g.render()


@dataclass(slots=True, kw_only=True)
class Stop(Element):
    name = "stop"
    props = ("offset",)

    offset: float

    def render_offset(self):
        return f"{int(self.offset * 100)}%"


@dataclass(slots=True, kw_only=True)
class LinearGradient(Element):
    name = "linearGradient"
    props = ("x1", "y1", "x2", "y2")

    x1: float
    x2: float
    y1: float
    y2: float


@dataclass(slots=True, kw_only=True)
class RadialGradient(Element):
    name = "radialGradient"
    props = ("cx", "cy", "r")

    cx: float
    cy: float
    r: float

    def render_cx(self):
        return f"{int(self.cx * 100)}%"

    def render_cy(self):
        return f"{int(self.cy * 100)}%"

    def render_r(self):
        return f"{int(self.r * 100)}%"


def render(element: Element, indent: int = 0, text_as_path: bool = False) -> str:
    pad = "  " * indent

    attrs = {}
    if element.id is not None:
        attrs["id"] = element.id

    for p in element.props:
        if hasattr(element, f"render_{p}"):
            attrs[p] = getattr(element, f"render_{p}")()
        elif getattr(element, p) is not None:
            attrs[p] = str(getattr(element, p))

    if element.attrs:
        attrs.update(element.attrs)
    attr_str = "".join(f' {k}="{v}"' for k, v in attrs.items())

    if not element.children and not isinstance(element, Text):
        return f"{pad}<{element.name}{attr_str} />"

    if isinstance(element, Text) and text_as_path:
        return element.render_as_path()

    elif isinstance(element, Text):
        inner = element.text

    elif element.children:
        children = '\n'.join(c.render(indent + 1, text_as_path=text_as_path) for c in element.children)
        inner = f"\n{children}\n{pad}"

    else:
        inner = ""

    return f"{pad}<{element.name}{attr_str}>{inner}</{element.name}>"
