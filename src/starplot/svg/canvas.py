from enum import Enum
from pathlib import Path

import numpy as np
from pyproj import CRS, Transformer
from shapely import Polygon as ShapelyPolygon, LineString
from shapely.ops import transform as _transform_shape

from starplot import geometry as _geometry
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
from starplot.projections import ProjectionBase, latlon_bounds_to_projection
from starplot.svg import symbols, png
from starplot.svg.elements import (
    SVG,
    Group,
    Rectangle,
    ClipPath,
    Polygon,
    Polyline,
    Text,
    Defs,
    LinearGradient,
    RadialGradient,
    Stop,
)


CRS_WNU = CRS.from_proj4("+proj=latlon +ellps=sphere +axis=wnu +a=6378137")


class CoordinateSystem(str, Enum):
    DATA = "data"
    PROJECTED = "projected"
    AXES = "axes"
    DISPLAY = "display"


def normalize(value, min_val, max_val):
    return (value - min_val) / (max_val - min_val)


class Canvas:
    """

    Args:
        bounds: Bounds in data coordinates (left, bottom, right, top)
    """

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
        self.elements = []
        self.figure_elements = []
        self.defs = []
        self.def_ids = set()

        self.axes_x = 0
        self.axes_y = 0

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
        self._init_clip_path_background()

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

        if self.invert_x:
            x = self.width - x

        if self.invert_y:
            y = self.height - y
        
        return np.round(x, self.precision), np.round(y, self.precision)

    def _is_global(self):
        return (
            abs(self.bounds[0] - self.bounds[2]) >= 360
            and abs(self.bounds[1] - self.bounds[3]) >= 180
        )

    def _init_bounds(self):
        if self._is_global() or self.projection.global_only:
            self.minx, self.miny, self.maxx, self.maxy = self.projection.global_bounds
            self.projected_bounds = self.minx, self.miny, self.maxx, self.maxy
            self.bounds = 0.0000001, -90, 359.999999, 90
        else:
            self.minx, self.miny, self.maxx, self.maxy = latlon_bounds_to_projection(
                *self.bounds,
                target_crs=self.projection._crs,
            )
            self.projected_bounds = self.minx, self.miny, self.maxx, self.maxy
            self.bounds = self.tx.transform_bounds(
                *self.projected_bounds, direction="INVERSE"
            )

        # self.minx, self.miny, self.maxx, self.maxy = self.tx.transform_bounds(
        #     *self.bounds, densify_pts=100
        # )

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

        self.figure_height = self.height + self.style.figure_padding * 2
        self.figure_width = self.width + self.style.figure_padding * 2
        self.axes_x = self.style.figure_padding
        self.axes_y = self.style.figure_padding

        self.logger.debug(f"Projection = {self.projection.__class__.__name__.upper()}")
        self.logger.debug(f"Bounds = {self.bounds}")
        self.logger.debug(f"Extent (X) = {int(self.minx)} >> {int(self.maxx)}")
        self.logger.debug(f"Extent (Y) = {int(self.miny)} >> {int(self.maxy)}")
        self.logger.debug(f"Size (h X w) = {int(self.height)} x {self.width}")

    def _init_clip_path_background(self):
        if self.clip_path is not None:
            self.clip_path_display = _transform_shape(self._to_display, self.clip_path)
        else:
            self._clip_path_from_bounds()

        if self.style.has_gradient_background():
            gradient_id = "axes-background-gradient"
            stops = [
                Stop(offset=offset, attrs={"stop-color": color})
                for offset, color in self.style.background_color
            ]

            if self.style.background_gradient_direction == GradientDirection.RADIAL:
                gradient = RadialGradient(
                    id=gradient_id,
                    cx=0.5,
                    cy=0.5,
                    r=0.5,
                    children=stops,
                )
            else:
                gradient = LinearGradient(
                    id=gradient_id,
                    x1=0,
                    y1=1,
                    x2=0,
                    y2=0,
                    children=stops,
                )

            self._add_def(
                def_id=gradient_id,
                value=gradient,
            )
            fill = f"url(#{gradient_id})"
        else:
            fill = self.style.background_color.as_hex()

        dxy = list(self.clip_path_display.exterior.coords)
        self.background_element = Polygon(
            id="axes-background",
            points=dxy,
            attrs={
                "fill": fill,
            },
        )
        self.elements.append(
            (
                -1_000_000,
                self.background_element,
            )
        )

        axes_clip_path_id = "axes-clip-path"
        axes_clip_path = ClipPath(
            id=axes_clip_path_id, children=[self.background_element]
        )
        self._add_def(
            def_id=axes_clip_path_id,
            value=axes_clip_path,
        )

    def _clip_path_from_bounds(self):
        x0, y0, x1, y1 = self.bounds
        coords = _geometry.extent_polygon(x0, x1, y0, y1, n=1_000)
        xs, ys = coords[:, 0], coords[:, 1]

        dx, dy = self._to_display(xs, ys)
        dxy = list(zip(dx, dy))

        coords = np.array(dxy)
        diffs = np.diff(coords, axis=0)  # (N-1, 2) step vectors
        distances = np.hypot(diffs[:, 0], diffs[:, 1])  # (N-1,) euclidean distances
        keep = np.concatenate([[True], distances >= 1])  # always keep first point
        dxy = coords[keep]
        dxy = list(dxy)

        self.clip_path_display = ShapelyPolygon(dxy)

    def _add_def(self, def_id: str, value: str):
        if def_id in self.def_ids:
            return
        self.defs.append(value)
        self.def_ids.add(def_id)

    def marker(self, x, y, style: MarkerStyle) -> None:
        dx, dy = self._to_display(x, y)

        element = symbols.create(
            dx, dy, style.size * self.scale, style.symbol, style.css(self.scale)
        )
        self.elements.append((style.zorder, element))

    def markers(self, x, y, style: MarkerStyle, gid: str = None, sizes=None) -> None:
        dx, dy = self._to_display(x, y)
        gid = gid or "markers"
        sizes = sizes or []

        elements = [
            symbols.create(x, y, size * self.scale, style.symbol, None)
            for x, y, size in list(zip(dx, dy, sizes))
        ]

        self.elements.append(
            (
                style.zorder,
                Group(id=gid, attrs=style.css(self.scale), children=elements),
            )
        )

    def line(
        self,
        coordinates: list[tuple[float, float]] = None,
        style: PathStyle | LineStyle = None,
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

            attrs = style.css(self.scale)
            self.elements.append((style.zorder, Polyline(points=dxy, attrs=attrs)))

    def polygon(
        self,
        coordinates: list[tuple[float, float]],
        style: PolygonStyle,
        cs: CoordinateSystem = CoordinateSystem.DATA,
        attrs: dict = None,
    ) -> None:
        arr = np.array(coordinates)
        xs, ys = arr[:, 0], arr[:, 1]
        dx, dy = self._to_display(xs, ys, cs)
        dxy = list(zip(dx, dy))
        attrs = attrs or {}
        _attrs = {**style.css(self.scale), **attrs}

        self.elements.append((style.zorder, Polygon(points=dxy, attrs=_attrs)))

    def text(
        self,
        x: float,
        y: float,
        value: str,
        style: LabelStyle,
        angle: float = 0,
        cs: CoordinateSystem = CoordinateSystem.DATA,
        attrs: dict = None,
    ) -> None:
        """Plots text, with an optional rotation angle."""
        dx, dy = self._to_display(x, y, cs)

        attrs = attrs or {}
        _attrs = {**style.css(self.scale), **attrs}

        if angle:
            _attrs["transform"] = f"rotate({angle}, {dx}, {dy})"

        self.elements.append((style.zorder, Text(x=dx, y=dy, attrs=_attrs, text=value)))

    def title(
        self,
        value: str,
        style: LabelStyle,
    ) -> None:
        dx = self.figure_width / 2
        dy = self.style.figure_padding + style.font_size

        _attrs = {**style.css(self.scale), "text-anchor": "middle"}

        element = Text(x=dx, y=dy, attrs=_attrs, text=value)

        self.figure_elements.append((style.zorder, element))

        self.figure_height += self.style.figure_padding + style.font_size
        self.axes_y += self.style.figure_padding + style.font_size

    def render(self, text_as_path: bool = False) -> str:
        """Renders the canvas to an SVG string"""

        axes_sorted_by_z = sorted(self.elements, key=lambda e: e[0])
        axes_elements = [e for _, e in axes_sorted_by_z]
        axes_svg = SVG(
            x=self.axes_x,
            y=self.axes_y,
            height=self.height,
            width=self.width,
            children=[
                Defs(children=self.defs),
                Group(
                    id="axes",
                    attrs={
                        "clip-path": "url(#axes-clip-path)",
                    },
                    children=axes_elements,
                ),
            ],
        )

        figure_sorted_by_z = sorted(self.figure_elements, key=lambda e: e[0])
        figure_elements = [e for _, e in figure_sorted_by_z]
        figure_svg = SVG(
            height=self.figure_height,
            width=self.figure_width,
            children=[
                Rectangle(
                    x=0,
                    y=0,
                    height=self.figure_height,
                    width=self.figure_width,
                    attrs={"fill": self.style.figure_background_color.as_hex()},
                ),
                *figure_elements,
                axes_svg,
            ],
        )
        return figure_svg.render(text_as_path=text_as_path)

    def export(self, filename: str | Path, text_as_path: bool = False) -> None:
        """
        Exports the SVG to an SVG or PNG file. Type is inferred by filename.
        """
        if filename.endswith("png"):
            png.export_png_cairo(
                filename=filename, svg_source=self.render(text_as_path=True)
            )
            return

        with open(filename, "w", buffering=1024 * 1024) as outfile:
            outfile.write(self.render(text_as_path=text_as_path))
