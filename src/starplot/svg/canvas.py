from enum import Enum
from pathlib import Path

import numpy as np
from pyproj import CRS, Transformer
from shapely import Polygon, LineString

from starplot import geometry as _geometry
from starplot.config import settings as StarplotSettings, SvgTextType
from starplot.styles import (
    PlotStyle,
    MarkerStyle,
    ObjectStyle,
    LabelStyle,
    MarkerSymbolEnum,
    PathStyle,
    LineStyle,
    PolygonStyle,
    GradientDirection,
    AnchorPointEnum,
)
from starplot.plotters.text import CollisionHandler
from starplot.projections import ProjectionBase
from starplot.svg import symbols


CRS_WNU = CRS.from_proj4("+proj=latlon +ellps=sphere +axis=wnu +a=6378137")


class CoordinateSystem(str, Enum):
    DATA = "data"
    PROJECTED = "projected"
    AXES = "axes"
    DISPLAY = "display"


def normalize(value, min_val, max_val):
    return (value - min_val) / (max_val - min_val)


class Canvas:
    resolution: int

    projection: ProjectionBase

    tx: Transformer

    bounds: tuple[float, float, float, float]
    """
    Bounds in data coordinates
    
    (left, bottom, right, top)

    """

    style: PlotStyle

    invert_x: bool = False
    invert_y: bool = False

    height: int = None
    width: int = None

    precision: int

    symbols: set = set()
    symbol_ids = set()

    elements: list[tuple[int, str]] = []

    def __init__(
        self,
        resolution: int,
        projection: ProjectionBase,
        bounds: tuple[float, float, float, float],
        style: PlotStyle,
        scale: float = 1.0,
        clip_path=None,
        invert_x: bool = False,
        invert_y: bool = False,
        crs: CRS = None,
        debug: bool = False,
        precision: int = 2,
        logger=None,
    ):
        self.crs = crs or CRS_WNU
        self.resolution = resolution
        self.projection = projection
        self.bounds = bounds
        self.style = style
        self.scale = scale
        self.precision = precision
        self.debug = debug

        self.clip_path = clip_path

        self.invert_x = invert_x
        self.invert_y = invert_y

        self.tx = Transformer.from_crs(self.crs, self.projection._crs, always_xy=True)

        self.logger = logger

        self._init_bounds()

    def _to_axes(self, x, y):
        px, py = self.tx.transform(x, y)
        return normalize(px, self.minx, self.maxx), normalize(py, self.miny, self.maxy)

    def _to_display(self, x, y, cs: CoordinateSystem = CoordinateSystem.DATA):
        if cs == CoordinateSystem.DISPLAY:
            return x, y

        if cs == CoordinateSystem.AXES:
            ax, ay = x, y
        elif cs == CoordinateSystem.DATA:
            ax, ay = self._to_axes(x, y)
        elif cs == CoordinateSystem.PROJECTED:
            ax, ay = normalize(x, self.minx, self.maxx), normalize(
                y, self.miny, self.maxy
            )
        else:
            raise ValueError(f"Unrecognized coordinate system: {cs}")

        x = ax * self.width
        y = (1 - ay) * self.height
        if self.precision == 0:
            return x.astype(int), y.astype(int)
        return np.round(x, self.precision), np.round(y, self.precision)

    def _is_global(self):
        return abs(self.bounds[0] - self.bounds[2]) >= 360

    def _init_bounds(self):
        # if self._is_global():
        #     self.minx, _, self.maxx, _ = self.projection.bounds
        #     _, self.miny, _, self.maxy = self.tx.transform_bounds(*self.bounds)
        # else:
        #     self.minx, self.miny, self.maxx, self.maxy = self.tx.transform_bounds(*self.bounds)

        self.minx, self.miny, self.maxx, self.maxy = self.tx.transform_bounds(
            *self.bounds, densify_pts=100
        )
        self.projected_bounds = self.minx, self.miny, self.maxx, self.maxy

        span_x = abs(self.maxx - self.minx)
        span_y = abs(self.maxy - self.miny)

        if span_x > span_y:
            ratio = span_x / span_y
            self.width = self.resolution
            self.height = self.width / ratio
        else:
            ratio = span_y / span_x
            self.height = self.resolution
            self.width = self.height / ratio

        self.bounds = self.tx.transform_bounds(
            *self.projected_bounds, direction="INVERSE"
        )

        self.logger.debug(f"Projection = {self.projection.__class__.__name__.upper()}")
        self.logger.debug(f"Bounds = {self.bounds}")
        self.logger.debug(f"Extent (X) = {int(self.minx)} >> {int(self.maxx)}")
        self.logger.debug(f"Size (h X w) = {int(self.height)} x {self.width}")

    def _register_symbol(self, symbol_id: str, value: str):
        if symbol_id in self.symbol_ids:
            return
        self.symbols.add(value)
        self.symbol_ids.add(symbol_id)

    def marker(self, x, y, style: MarkerStyle) -> None:
        dx, dy = self._to_display(x, y)

        css = " ".join([f'{k}="{v}"' for k, v in style.css().items()])

        marker_str = symbols.create(dx, dy, style.size * self.scale, style.symbol, css)
        self.elements.append((style.zorder, marker_str))

    def markers(self, x, y, style: MarkerStyle, gid: str = None, sizes=None) -> None:
        dx, dy = self._to_display(x, y)

        css = " ".join([f'{k}="{v}"' for k, v in style.css().items()])

        gid = gid or "markers"
        sizes = sizes or []

        elements = "\n".join(
            [
                symbols.create(x, y, size * self.scale, style.symbol, "")
                for x, y, size in list(zip(dx, dy, sizes))
            ]
        )

        group = f'<g id="{gid}" {css}>\n{elements}</g>\n'

        self.elements.append((style.zorder, group))

    def line(
        self,
        coordinates: list[tuple[float, float]] = None,
        style: PathStyle | LineStyle = None,
        label: str = None,
        num_labels: int = 2,
        collision_handler: CollisionHandler = None,
    ) -> None:
        if self.projection.edge_x is not None:
            lines = _geometry.split_line_at_x(
                coordinates, self.projection.edge_x, offset=0.00001
            )
        else:
            lines = [coordinates]

        for line in lines:
            arr = np.array(line)
            xs, ys = arr[:, 0], arr[:, 1]
            dx, dy = self._to_display(xs, ys)
            dxy = list(zip(dx, dy))

            points = " ".join([f"{x},{y}" for x, y in dxy])

            if isinstance(style, LineStyle):
                attrs = " ".join([f'{k}="{v}"' for k, v in style.css().items()])
                z = style.zorder
            else:
                attrs = " ".join([f'{k}="{v}"' for k, v in style.line.css().items()])
                z = style.line.zorder

            self.elements.append((z, f'<polyline points="{points}" {attrs} />'))

    def polygon(
        self,
        coordinates: list[tuple[float, float]],
        style: PolygonStyle,
        cs: CoordinateSystem = CoordinateSystem.DATA,
        attrs: dict = None,
    ) -> float:
        arr = np.array(coordinates)
        xs, ys = arr[:, 0], arr[:, 1]
        dx, dy = self._to_display(xs, ys, cs)
        dxy = list(zip(dx, dy))

        points = " ".join([f"{x},{y}" for x, y in dxy])
        attrs_rendered = " ".join([f'{k}="{v}"' for k, v in style.css().items()])

        if attrs:
            attrs_rendered += " " + " ".join([f'{k}="{v}"' for k, v in attrs.items()])

        self.elements.append(
            (style.zorder, f'<polygon points="{points}" {attrs_rendered} />')
        )

    def text(
        self,
        x,
        y,
        value: str,
        style: LabelStyle,
        angle: float = 0,
        cs: CoordinateSystem = CoordinateSystem.DATA,
        attrs: dict = None,
    ) -> float:
        """Plots text, with an optional rotation angle."""
        dx, dy = self._to_display(x, y, cs)
        attrs_rendered = " ".join([f'{k}="{v}"' for k, v in style.css().items()])

        if angle:
            attrs_rendered += f' transform="rotate({angle}, {dx}, {dy})"'

        if attrs:
            attrs_rendered += " " + " ".join([f'{k}="{v}"' for k, v in attrs.items()])

        self.elements.append(
            (style.zorder, f'<text x="{dx}" y="{dy}" {attrs_rendered} >{value}</text>')
        )

    def _background(self):
        self.elements.append(
            (
                -1_000_000,
                f'<rect x="-100" y="-100" height="{self.height+200}" width="{self.width+200}" fill="{self.style.background_color.as_hex()}" />',
            )
        )

    def _rectangle(self, x, y, height, width, color, stroke_width=1):
        self.elements.append(
            (
                1_000_000,
                f'<rect x="{x}" y="{y}" height="{height}" width="{width}" fill="none" stroke="{color}" stroke-width="{stroke_width}" />',
            )
        )

    def render(self, pretty: bool = False) -> str:
        """Renders the canvas to an SVG string"""
        result = f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.width}" height="{self.height}" viewBox="0 0 {self.width} {self.height}">'

        if self.symbols:
            result += "\n\n<defs>\n"
            for symbol in self.symbols:
                result += f"{symbol}\n"
            result += "</defs>\n\n"

        sorted_by_z = sorted(self.elements, key=lambda e: e[0])
        elements = [e for _, e in sorted_by_z]
        result += "\n".join(elements) + "</svg>"

        if pretty:
            import xml.dom.minidom

            result = xml.dom.minidom.parseString(result).toprettyxml(indent="  ")

        return result

    def export(self, filename: str | Path, pretty: bool = False) -> None:
        """
        Exports the SVG to an SVG or PNG file. Type is inferred by filename.
        """
        if filename.endswith("png"):
            from resvg_py import svg_to_bytes

            # import cairosvg
            # cairosvg.svg2png(self.render(), write_to=filename)
            # return

            png_bytes = svg_to_bytes(svg_string=self.render())

            with open(filename, "wb") as f:
                f.write(png_bytes)

            return

        with open(filename, "w", buffering=1024 * 1024) as outfile:
            outfile.write(self.render(pretty=pretty))
