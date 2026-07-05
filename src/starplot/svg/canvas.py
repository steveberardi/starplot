from enum import Enum
from pathlib import Path

import numpy as np
from shapely import Polygon as ShapelyPolygon, LineString, MultiPoint, Point
from shapely.ops import transform as _transform_shape
from shapely.affinity import translate as _translate_shape

from pyproj import CRS

from starplot import geometry as _geometry
from starplot.styles import (
    PlotStyle,
    MarkerStyle,
    LabelStyle,
    PathStyle,
    LineStyle,
    PolygonStyle,
    GradientDirection,
    LegendStyle,
)
from starplot.projections import (
    ProjectionBase,
    latlon_bounds_to_projection,
    CoordinateReferenceSystem,
)
from starplot.svg import symbols, png
from starplot.svg.layout import Layout, Region, LegendRegion
from starplot.svg.elements import (
    Group,
    Rectangle,
    ClipPath,
    Polygon,
    Polyline,
    Text,
    LinearGradient,
    RadialGradient,
    Stop,
)


class CoordinateSystem(str, Enum):
    DATA = "data"
    PROJECTED = "projected"
    AXES = "axes"
    DISPLAY = "display"
    FIGURE_DISPLAY = "figure_display"


def normalize(value, min_val, max_val):
    return (value - min_val) / (max_val - min_val)


def lerp(start: float, end: float, t: float) -> float:
    """
    Linear interpolation between two numbers.

    Args:
        start: The starting value
        end: The ending value
        t: The interpolation factor (0.0 = start, 1.0 = end)

    Returns:
        The interpolated value between start and end
    """
    return start + (end - start) * t


def get_text_hw(text, font_size: int, font_weight: int = 400) -> tuple[float, float]:
    char_width = font_size * (0.65 if font_weight >= 500 else 0.6)
    width = len(text) * char_width
    height = font_size
    return height, width


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
        crs: CoordinateReferenceSystem = None,
        debug: bool = False,
        precision: int = 2,
        logger=None,
    ):
        self.layout = Layout()
        self.crs = CRS.from_proj4(crs.value or CoordinateReferenceSystem.ENU.value)
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

        self.tx = self.projection.get_transformer(source_crs=self.crs)

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
        if self.clip_path:
            self.minx, self.miny, self.maxx, self.maxy = self.tx.transform_bounds(
                *self.clip_path.bounds, densify_pts=1_000
            )
            # self.minx, self.miny, self.maxx, self.maxy = latlon_bounds_to_projection(
            #     *self.bounds,
            #     source_crs=self.crs,
            #     target_crs=self.projection.get_crs(source_crs=self.crs),
            # )
            self.projected_bounds = self.minx, self.miny, self.maxx, self.maxy
            self.bounds = self.tx.transform_bounds(
                *self.projected_bounds, direction="INVERSE"
            )
        elif self._is_global() or self.projection.global_only:
            self.minx, self.miny, self.maxx, self.maxy = self.projection.global_bounds
            self.projected_bounds = self.minx, self.miny, self.maxx, self.maxy
            self.bounds = 0.0000001, -90, 359.999999, 90
        else:
            if self.bounds[0] == 0:
                self.bounds[0] = 0.00001
            if self.bounds[2] == 0:
                self.bounds[0] = 360 - 0.00001

            self.minx, self.miny, self.maxx, self.maxy = latlon_bounds_to_projection(
                *self.bounds,
                source_crs=self.crs,
                target_crs=self.projection.get_crs(source_crs=self.crs),
            )
            # print("original: ", self.bounds)
            # self.minx, self.miny, self.maxx, self.maxy = self.tx.transform_bounds(
            #     *self.bounds, densify_pts=100
            # )
            self.projected_bounds = self.minx, self.miny, self.maxx, self.maxy
            self.bounds = self.tx.transform_bounds(
                *self.projected_bounds, direction="INVERSE"
            )
            # print("new: ", self.bounds)

        self._refresh_figure_dimensions()

        self.logger.debug(f"Projection = {self.projection.__class__.__name__.upper()}")
        self.logger.debug(f"Bounds = {self.bounds}")
        self.logger.debug(f"Extent (X) = {int(self.minx)} >> {int(self.maxx)}")
        self.logger.debug(f"Extent (Y) = {int(self.miny)} >> {int(self.maxy)}")
        self.logger.debug(f"Size (h X w) = {int(self.height)} x {self.width}")

    def _refresh_figure_dimensions(self):
        span_x = abs(self.maxx - self.minx)
        span_y = abs(self.maxy - self.miny)

        if span_x > span_y:
            ratio = span_x / span_y
            self.width = self.resolution
            self.height = self.width / ratio

            self.layout.axes.width = self.resolution
            self.layout.axes.height = self.layout.axes.width / ratio
        else:
            ratio = span_y / span_x
            self.height = self.resolution
            self.width = self.height / ratio

            self.layout.axes.height = self.resolution
            self.layout.axes.width = self.layout.axes.height / ratio

    def _init_clip_path_background(self):
        """
        TODO:
        - display bounds based on user provided min/max ranges OR clip path
        - query bounds based on transformation bounds

        """
        if self.clip_path is not None:
            self.clip_path_display = _transform_shape(self._to_display, self.clip_path)
            dx0, dy0, dx1, dy1 = self.clip_path_display.bounds

            ax0 = dx0 / self.width
            ax1 = dx1 / self.width
            ay0 = dy0 / self.height
            ay1 = dy1 / self.height

            minx, maxx = self.minx, self.maxx
            self.minx = lerp(minx, maxx, ax0)
            self.maxx = lerp(minx, maxx, ax1)

            maxy, miny = self.maxy, self.miny
            self.miny = lerp(maxy, miny, ay1)
            self.maxy = lerp(maxy, miny, ay0)

            self.projected_bounds = self.minx, self.miny, self.maxx, self.maxy
            self.bounds = self.tx.transform_bounds(
                *self.projected_bounds, direction="INVERSE"
            )

            self._refresh_figure_dimensions()

            # we changed the figure dimensions so we have to re-calculate clip path display coords
            self.clip_path_display = _transform_shape(self._to_display, self.clip_path)
            self.logger.debug(
                f"Adjusted Size (h X w) = {int(self.height)} x {self.width}"
            )

        elif self.projection.curved:
            xs, ys = zip(*self.projection.global_clip_path())
            dx, dy = self._to_display(np.array(xs), np.array(ys))
            dxy = list(zip(dx, dy))

            self.clip_path_display = ShapelyPolygon(dxy)
            #     pass
            # self._clip_path_from_bounds()
            # TODO : fix this function above
        else:
            self.clip_path_display = ShapelyPolygon(
                [
                    (0, 0),
                    (self.width, 0),
                    (self.width, self.height),
                    (0, self.height),
                ]
            )

        if self.style.axes.has_gradient_background():
            gradient_id = "axes-background-gradient"
            stops = [
                Stop(offset=offset, attrs={"stop-color": color})
                for offset, color in self.style.axes.background_color
            ]

            if (
                self.style.axes.background_gradient_direction
                == GradientDirection.RADIAL
            ):
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

            self.defs.append(gradient)
            self.layout.axes.defs.append(gradient)
            fill = f"url(#{gradient_id})"
        else:
            fill = self.style.axes.background_color.as_hex()

        dxy = list(self.clip_path_display.exterior.coords)
        self.background_element = Polygon(
            id="axes-background",
            points=dxy,
            attrs={
                "fill": fill,
            },
        )
        self.layout.axes.elements.append(
            (
                -1_000_000,
                self.background_element,
            )
        )
        axes_clip_path_id = "axes-clip-path"
        axes_clip_path = ClipPath(
            id=axes_clip_path_id, children=[self.background_element]
        )
        self.layout.axes.defs.append(axes_clip_path)

    def _clip_path_from_bounds(self):
        """DEPRECATED"""
        x0, y0, x1, y1 = self.bounds
        coords = _geometry.extent_polygon(x0, x1, y0, y1, n=100)
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

    def marker(self, x, y, style: MarkerStyle) -> None:
        dx, dy = self._to_display(x, y)
        element = symbols.create(
            dx, dy, style.size * self.scale, style.symbol, style.css(self.scale)
        )
        self.layout.axes.elements.append((style.zorder, element))

    def markers(self, x, y, style: MarkerStyle, gid: str = None, sizes=None) -> None:
        dx, dy = self._to_display(x, y)
        gid = gid or "markers"
        sizes = sizes or []

        elements = [
            symbols.create(x, y, size * self.scale, style.symbol, None)
            for x, y, size in list(zip(dx, dy, sizes))
        ]
        self.layout.axes.elements.append(
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
            # split at antimeridian AND edge_x
            lines = []
            lines_antimeridian = _geometry.split_at_antimeridian(
                coordinates,
                offset=0.0001,
            )
            for line in lines_antimeridian:
                lines_edge_x = _geometry.split_line_at_x(
                    line, self.projection.edge_x, offset=0.0001
                )
                lines.extend(lines_edge_x)

        else:
            lines = [coordinates]

        for line in lines:
            arr = np.array(line)
            xs, ys = arr[:, 0], arr[:, 1]
            dx, dy = self._to_display(xs, ys)
            dxy = list(zip(dx, dy))

            attrs = style.css(self.scale)
            self.layout.axes.elements.append(
                (style.zorder, Polyline(points=dxy, attrs=attrs))
            )

    def polygon(
        self,
        coordinates: list[tuple[float, float]],
        style: PolygonStyle,
        cs: CoordinateSystem = CoordinateSystem.DATA,
        attrs: dict = None,
    ) -> None:
        """
        TODO : better split for polygons and lines

        1. Split list of coords at antimeridian and edge_x
        2. For each list from the split, convert to display coords
        3. Combine lists (in order)
        4. Plot as one polygon or line

        ^^ wont work for wrapping
        """

        polygons = []
        # polygons_am = _geometry.split_at_antimeridian(coordinates, offset=0.01)

        lines_edge_x = _geometry.split_line_at_x(
            coordinates, self.projection.edge_x, offset=0.01
        )
        polygons.extend(lines_edge_x)

        for polygon_coords in polygons:
            arr = np.array(polygon_coords)
            xs, ys = arr[:, 0], arr[:, 1]
            dx, dy = self._to_display(xs, ys, cs)
            dxy = list(zip(dx, dy))
            attrs = attrs or {}
            _attrs = {**style.css(self.scale), **attrs}

            self.layout.axes.elements.append(
                (style.zorder, Polygon(points=dxy, attrs=_attrs))
            )

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

        self.layout.axes.elements.append(
            (style.zorder, Text(x=dx, y=dy, attrs=_attrs, text=value))
        )

    def title(
        self,
        value: str,
        style: LabelStyle,
    ) -> None:
        _attrs = {
            **style.css(self.scale),
            "text-anchor": "middle",
            "dominant-baseline": "central",
        }
        self.layout.title = Region(
            elements=[
                (
                    style.zorder,
                    Text(
                        x=(self.layout.axes.width + self.style.figure.padding * 2) / 2,
                        y=0,
                        attrs=_attrs,
                        text=value,
                    ),
                )
            ],
            height=style.font_size + style.padding_bottom,
            width=self.layout.axes.width,
        )

    def legend(
        self,
        sections: list[tuple[str, dict]],
        style: LegendStyle,
    ) -> None:
        """
        Plots a legend with one or more sections

        Args:
            sections: List of sections for the legend, in the format (title, handles)
            style: Styling properties for the legend (applies to all sections)
        """
        x = style.padding_x
        y = style.padding_y
        height = style.padding_y * 2
        width = style.padding_x * 2
        sections_elements = []
        title_element = None

        for i, value in enumerate(sections):
            title, handles = value
            if title:
                h, w = get_text_hw(
                    title,
                    font_size=style.title.font_size * self.scale,
                    font_weight=style.title.font_weight,
                )
                y += h
                title_element = Text(
                    x=x, y=y, text=title, attrs=style.title.css(self.scale)
                )
                sections_elements.append(title_element)
                height += h * 2 + style.label_padding
                width = max(width, w * 1.5)
                y += h + style.label_padding / 2
            else:
                y += style.label_padding / 2

            for label, config in handles.items():
                marker_style, size = config
                marker_size = size or style.symbol_size
                marker_element = symbols.create(
                    x + style.symbol_size / 2,
                    y,
                    marker_size * self.scale,
                    marker_style.symbol,
                    marker_style.css(self.scale),
                )

                y += style.symbol_size / 2
                label_x = x + style.symbol_size * self.scale + style.symbol_padding
                label_attrs = style.labels.css(self.scale)
                label_element = Text(x=label_x, y=y, text=label, attrs=label_attrs)

                sections_elements.append(
                    Group(
                        children=[marker_element, label_element],
                    )
                )

                h, w = get_text_hw(
                    label,
                    font_size=style.labels.font_size * self.scale,
                    font_weight=style.labels.font_weight,
                )
                height += (
                    max(marker_size * self.scale, style.symbol_size * self.scale, h)
                    + style.label_padding
                )
                width = max(width, w * 1.3)
                y += h + style.label_padding

            if i < len(sections) - 1:
                height += style.label_padding * 2.5
            else:
                height += style.label_padding

        background_element = Rectangle(
            x=0,
            y=0,
            height=height,
            width=width,
            attrs={
                "fill": style.background_color.as_hex(),
                "stroke": style.border_color.as_hex(),
                "stroke-width": style.border_width,
                "rx": style.border_radius,
            },
        )

        self.layout.legend = LegendRegion(
            elements=[
                (0, background_element),
                *[(1, e) for e in sections_elements],
            ],
            height=height,
            width=width,
            location=style.location,
            margin_x=style.margin_x,
            margin_y=style.margin_y,
        )

    def _clip_path_border(self, style: PathStyle, labels: list = None) -> None:
        """
        Creates a border around the axes clip path. The border is plotted as a line element.

        Args:
            style: Style of border line
            labels: List of 2-tuples where the first item is a list of coordinates for a line that intersects the border,
                    and the second item is a string label for that intersection.

        TODO : add way to restrict label points to only top/bottom or left/right
        """
        label_elements = []

        border = self.clip_path_display.buffer(style.line.width / 2)

        bx1, by1, bx2, by2 = border.bounds
        cx1, cy1, cx2, cy2 = self.clip_path_display.bounds
        xoff = (bx2 - bx1) - (cx2 - cx1)
        yoff = (by2 - by1) - (cy2 - cy1)

        border = _translate_shape(border, xoff=xoff, yoff=yoff)
        coords = list(zip(*border.exterior.coords.xy))
        border_line = LineString(coords)
        attrs = style.line.css(self.scale)

        if self.debug:
            label_elements.append(
                (
                    10_000_000_000,
                    Polyline(
                        points=list(zip(*self.clip_path_display.exterior.coords.xy)),
                        attrs=LineStyle(color="red", width=4, zorder=1_000_000).css(
                            self.scale
                        ),
                    ),
                )
            )
            label_elements.append(
                (
                    10_000_000_000,
                    Polyline(
                        points=list(zip(*border.exterior.coords.xy)),
                        attrs=LineStyle(color="#1effff", width=2, zorder=1_000_000).css(
                            self.scale
                        ),
                    ),
                )
            )

        if labels:
            # 1. convert coordinates to display
            # 2. find intersection of line with border
            # 3. add text element at intersection

            for xy, text in labels:
                arr = np.array(xy)
                xs, ys = arr[:, 0], arr[:, 1]
                dx, dy = self._to_display(xs, ys)
                dxy = list(zip(dx, dy))

                # only works for clip paths that have offsets exactly equal to the line width for border
                dxy = [(x + xoff, y + yoff) for x, y in dxy]

                labeled_line = LineString(dxy)

                if self.debug:
                    label_elements.append(
                        (
                            10_000_000_000,
                            Polyline(
                                points=dxy,
                                attrs=LineStyle(
                                    color="#ff5aff", width=2, zorder=1_000_000
                                ).css(self.scale),
                            ),
                        )
                    )

                border_intersection = labeled_line.intersection(border_line)

                if isinstance(border_intersection, Point):
                    border_intersection = MultiPoint([border_intersection])
                elif not isinstance(border_intersection, MultiPoint):
                    continue

                for ix in border_intersection.geoms:
                    element = Text(
                        x=ix.x,
                        y=ix.y,
                        text=text,
                        attrs={
                            **style.label.css(self.scale),
                            "text-anchor": "middle",
                            "dominant-baseline": "central",
                        },
                    )
                    label_elements.append((style.line.zorder + 10, element))

        self.layout.axes_border = Region(
            elements=[
                (style.line.zorder, Polyline(points=coords, attrs=attrs)),
                *label_elements,
            ],
            height=self.layout.axes.height + style.line.width * 2,
            width=self.layout.axes.width + style.line.width * 2,
        )

    def render(self, text_as_path: bool = False) -> str:
        """Renders the canvas to an SVG string"""
        return self.layout.render(self.style, text_as_path)

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
