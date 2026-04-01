from dataclasses import dataclass, field
from typing import ClassVar


@dataclass(slots=True, kw_only=True)
class Element:
    name: ClassVar[str] = "none"
    props: ClassVar[tuple[str]] = ()

    id: str | None = None
    text: str | None = None

    attrs: dict = field(default_factory=dict)
    children: list["Element"] = field(default_factory=list)

    def render(self, indent: int = 0) -> str:
        pad = "  " * indent

        attrs = {}
        if self.id is not None:
            attrs["id"] = self.id

        for p in self.props:
            if hasattr(self, f"render_{p}"):
                attrs[p] = getattr(self, f"render_{p}")()
            elif getattr(self, p) is not None:
                attrs[p] = str(getattr(self, p))

        if self.attrs:
            attrs.update(self.attrs)
        attr_str = "".join(f' {k}="{v}"' for k, v in attrs.items())

        if not self.children and not self.text:
            return f"{pad}<{self.name}{attr_str} />"

        inner = self.text or ""
        children_str = "\n".join(c.render(indent + 1) for c in self.children)
        if children_str:
            inner = f"\n{children_str}\n{pad}"

        return f"{pad}<{self.name}{attr_str}>{inner}</{self.name}>"


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
class Text(Element):
    name = "text"
    props = ("x", "y")

    x: float
    y: float
