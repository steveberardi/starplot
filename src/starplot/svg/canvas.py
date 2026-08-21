import hashlib
import math
from contextlib import contextmanager
from enum import Enum
from pathlib import Path

import numpy as np
from pyproj import CRS
from shapely import LineString, MultiPoint, Point, box, concave_hull
from shapely import Polygon as ShapelyPolygon
from shapely.affinity import translate as _translate_shape
from shapely.ops import transform as _transform_shape

from starplot import geometry as _geometry
from starplot.projections import (
    CoordinateReferenceSystem,
    ProjectionBase,
    latlon_bounds_to_projection,
)
from starplot.styles import (
    GradientStops,
    GradientType,
    LabelStyle,
    LegendStyle,
    LineStyle,
    MarkerStyle,
    PathStyle,
    PlotStyle,
    PolygonStyle,
    TableStyle,
)
from starplot.svg import fonts, png, symbols
from starplot.svg.elements import (
    ClipPath,
    Group,
    Line,
    Polygon,
    Polyline,
    Rectangle,
    Text,
    create_gradient,
)
from starplot.svg.layout import Layout, LegendRegion, Region, TableRegion


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


def gradient_hash(stops, length=8) -> str:
    return hashlib.sha256(repr(stops).encode()).hexdigest()[:length]


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
        self.gradient_counter = 0
        self._group_stack: list[list[tuple[float, object]]] = []

        self.invert_x = invert_x
        self.invert_y = invert_y

        self.tx = self.projection.get_transformer(source_crs=self.crs)

        self.logger = logger

        self._init_bounds()
        self._init_clip_path_background()
        self._init_axes_border()

    def _to_axes(self, x, y):
        px, py = self.tx.transform(x, y)
        return normalize(px, self.minx, self.maxx), normalize(py, self.miny, self.maxy)

    @property
    def _max_projection_jump(self) -> float:
        """
        Distance (in projected units) above which two consecutive projected
        points are considered discontinuous -- i.e. on opposite sides of the
        projection's seam/pole rather than genuinely adjacent.
        """
        return 0.5 * max(self.maxx - self.minx, self.maxy - self.miny)

    def _to_display(self, x, y, cs: CoordinateSystem = CoordinateSystem.DATA):
        if cs == CoordinateSystem.DISPLAY:
            return x, y

        if cs == CoordinateSystem.AXES:
            ax, ay = x, y
        elif cs == CoordinateSystem.DATA:
            ax, ay = self._to_axes(x, y)
        elif cs == CoordinateSystem.PROJECTED:
            ax, ay = (
                normalize(x, self.minx, self.maxx),
                normalize(y, self.miny, self.maxy),
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
        return self.projection.global_only or (
            abs(self.bounds[0] - self.bounds[2]) >= 359
            and abs(self.bounds[1] - self.bounds[3]) >= 179
        )

    def _init_bounds(self):
        """
        Calculates true bounds from user-bounds, which can change slightly as a result of the map projection used.

        For example, supplying a bounding-box bounds for a stereographic projection will require growing the bounds a little.

        This function also handles snapping a bounds to a clip path, if the user supplied one.
        """
        if self.clip_path:
            self.minx, self.miny, self.maxx, self.maxy = self.tx.transform_bounds(
                *self.clip_path.bounds, densify_pts=1_000
            )
            self.projected_bounds = self.minx, self.miny, self.maxx, self.maxy
            self.bounds = self.tx.transform_bounds(
                *self.projected_bounds, direction="INVERSE"
            )
        elif self._is_global():
            self.minx, self.miny, self.maxx, self.maxy = self.projection.global_bounds
            self.projected_bounds = self.minx, self.miny, self.maxx, self.maxy
            self.bounds = 0.0000001, -90, 359.999999, 90
        else:
            if self.bounds[0] == 0:
                self.bounds[0] = 0.0000001

            if self.bounds[2] == 360:
                self.bounds[2] = 359.999999

            self.minx, self.miny, self.maxx, self.maxy = latlon_bounds_to_projection(
                *self.bounds,
                source_crs=self.crs,
                target_crs=self.projection.get_crs(source_crs=self.crs),
                curved=self.projection.curved,
                transformer=self.tx,
            )
            self.projected_bounds = self.minx, self.miny, self.maxx, self.maxy
            self.bounds = self.tx.transform_bounds(
                *self.projected_bounds, direction="INVERSE"
            )

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
        Initializes the clip path, which is either a user-provided path or simply the background of the axes
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
            self.clip_path_display = concave_hull(MultiPoint(dxy), ratio=0.3)

        else:
            self.clip_path_display = ShapelyPolygon(
                [
                    (0, 0),
                    (self.width, 0),
                    (self.width, self.height),
                    (0, self.height),
                ]
            )

        background_attrs = self.style.axes.background.css(self.scale)

        if isinstance(self.style.axes.background.fill, list):
            background_attrs["fill"] = self._get_or_create_gradient(
                stops=self.style.axes.background.fill,
                type=self.style.axes.background.gradient_type,
                id="axes-background-gradient",
            )

        dxy = list(self.clip_path_display.exterior.coords)
        self.background_element = Polygon(
            id="axes-background",
            points=dxy,
            attrs=background_attrs,
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
        self.layout.axes.defs[axes_clip_path_id] = axes_clip_path

    def _init_axes_border(self):
        """
        Draws the axes_border region: a border immediately outside the axes
        clip path. The entire stroke sits outside the clip path -- none of it
        overlaps the plot content. If the plot also has an axes_frame (e.g. from gridlines),
        that begins exactly where this border ends, with no overlap between the two.
        """
        self._axes_border_offset = 0
        style = self.style.axes.border

        if style is None:
            return

        border_width = style.width * self.scale
        self._axes_border_offset = border_width

        # buffer by half the stroke width so the centered stroke's inner edge
        # touches the clip path and its outer edge lands at clip_path + border_width
        # (join_style="mitre" keeps corners sharp instead of shapely's default round)
        ring = self.clip_path_display.buffer(border_width / 2, join_style="mitre")
        coords = list(ring.exterior.coords)

        outer = self.clip_path_display.buffer(border_width, join_style="mitre")
        bx1, by1, bx2, by2 = outer.bounds

        self.layout.axes_border = Region(
            elements=[
                (style.zorder, Polyline(points=coords, attrs=style.css(self.scale)))
            ],
            height=(by2 - by1),
            width=(bx2 - bx1),
        )

    def _get_or_create_gradient(
        self, stops: GradientStops, type: GradientType, id: str | None = None
    ) -> str:
        """
        Returns URL of gradient element with specified id, or creates and returns it if it doesn't exist.
        """
        gid = id or gradient_hash(stops)
        existing = self.layout.axes.defs.get(gid)

        if existing:
            return existing.url

        gradient = create_gradient(stops, type, gid)
        self.layout.axes.defs[gradient.id] = gradient
        return gradient.url

    def _add_element(self, zorder: float, element) -> None:
        """Appends an element to the currently active group (if any), else directly to the axes."""
        if self._group_stack:
            self._group_stack[-1].append((zorder, element))
        else:
            self.layout.axes.elements.append((zorder, element))

    @contextmanager
    def group(
        self,
        gid: str | None = None,
        attrs: dict | None = None,
        zorder: float | None = None,
    ):
        """
        Groups every element drawn within this context into a single SVG `<g>` element.

        Groups can be nested, in which case the inner group is added as a single element
        of the outer group.

        Args:
            gid: `id` attribute for the `<g>` element
            attrs: Additional attributes for the `<g>` element
            zorder: Zorder for the group itself (i.e. where it's positioned among its siblings). If `None`, then the lowest zorder of the group's elements will be used.
        """
        frame: list[tuple[float, object]] = []
        self._group_stack.append(frame)
        try:
            yield
        finally:
            self._group_stack.pop()

        if not frame:
            return

        frame.sort(key=lambda e: e[0])
        group_zorder = zorder if zorder is not None else frame[0][0]
        self._add_element(
            group_zorder,
            Group(id=gid, attrs=attrs or {}, children=[e for _, e in frame]),
        )

    def marker(self, x, y, style: MarkerStyle) -> None:
        dx, dy = self._to_display(x, y)

        attrs = style.css(self.scale)

        if isinstance(style.fill, list):
            attrs["fill"] = self._get_or_create_gradient(
                stops=style.fill,
                type=style.gradient_type,
            )

        element = symbols.create(
            dx, dy, style.size * self.scale, style.symbol, attrs=attrs
        )
        self._add_element(style.zorder, element)

    def markers(
        self,
        xs,
        ys,
        style: MarkerStyle,
        gid: str | None = None,
        sizes: list[float] | None = None,
        colors: list[str] | list[list[tuple[float, str]]] | None = None,
        opacity_values: list[float] | None = None,
    ) -> None:
        dx, dy = self._to_display(xs, ys)
        gid = gid or "markers"
        count = len(xs)
        sizes = sizes or [style.size] * count
        colors = colors or [style.fill] * count
        opacity_values = opacity_values or [style.opacity] * count
        elements = []

        for x, y, size, color, opacity in list(
            zip(dx, dy, sizes, colors, opacity_values)
        ):
            attrs = {}

            if isinstance(color, list):
                attrs["fill"] = self._get_or_create_gradient(
                    stops=color,
                    type=style.gradient_type,
                )
            else:
                attrs["fill"] = color

            if opacity != 1:
                attrs["fill-opacity"] = opacity

            element = symbols.create(
                x, y, size=size * self.scale, symbol=style.symbol, attrs=attrs
            )

            elements.append(element)

        self._add_element(
            style.zorder,
            Group(id=gid, attrs=style.css(self.scale), children=elements),
        )

    def _refine_jump(self, a, b):
        """
        A coarse jump between two *original* (RA/DEC) points doesn't mean
        the whole segment should be dropped -- for a densely-sampled curve
        (gridlines, the ecliptic) dropping the one small gap between two
        adjacent samples is imperceptible, but for a sparse line (e.g. a
        constellation edge, just 2 points total) it would silently delete
        the entire line. So re-sample the original a->b segment finely and
        re-run the same jump split at that resolution, giving each side a
        real line reaching almost all the way to the seam instead of
        nothing.
        """
        ra_a, ra_b = a[0], b[0]
        # interpolate along the *shorter* way around -- a plain linspace
        # between e.g. RA 359 and RA 1 would otherwise sweep the long way
        # through RA 180, cutting across the whole visible sky instead of
        # the real ~2-degree gap between them.
        if ra_b - ra_a > 180:
            ra_b -= 360
        elif ra_a - ra_b > 180:
            ra_b += 360

        ra = np.linspace(ra_a, ra_b, 64)
        dec = np.linspace(a[1], b[1], 64)
        rx, ry = self.tx.transform(ra, dec)
        return _geometry.split_line_at_projection_jumps(
            list(zip(rx, ry)), max_jump=self._max_projection_jump
        )

    def _split_line_with_refinement(self, coordinates, px, py):
        max_jump = self._max_projection_jump
        segments = []
        current = []

        for i, (x, y) in enumerate(zip(px, py)):
            finite = np.isfinite(x) and np.isfinite(y)

            if not finite:
                if current:
                    segments.append(current)
                    current = []
                continue

            if current:
                lx, ly = current[-1]
                if math.hypot(x - lx, y - ly) > max_jump:
                    refined = self._refine_jump(coordinates[i - 1], coordinates[i])
                    if not refined:
                        segments.append(current)
                        current = []
                    elif len(refined) == 1:
                        current.extend(refined[0])
                    else:
                        current.extend(refined[0])
                        segments.append(current)
                        segments.extend(refined[1:-1])
                        current = list(refined[-1])

            current.append((x, y))

        if current:
            segments.append(current)

        return segments

    def line(
        self,
        coordinates: list[tuple[float, float]] | None = None,
        style: PathStyle | LineStyle = None,
    ) -> None:
        arr = np.array(coordinates)
        px, py = self.tx.transform(arr[:, 0], arr[:, 1])

        if self.projection.wraps:
            # Cut wherever the *projected* line jumps or goes non-finite,
            # instead of guessing where the projection's seam falls in RA/DEC
            # space (that only has a simple answer for unrotated cylindrical
            # projections -- see ObliqueMercator, whose seam isn't a fixed RA).
            lines_split = self._split_line_with_refinement(coordinates, px, py)
        else:
            lines_split = [list(zip(px, py))]

        for line in lines_split:
            if len(line) < 2:
                continue

            arr = np.array(line)
            xs, ys = arr[:, 0], arr[:, 1]
            dx, dy = self._to_display(xs, ys, cs=CoordinateSystem.PROJECTED)
            dxy = list(zip(dx, dy))

            attrs = style.css(self.scale)
            self._add_element(style.zorder, Polyline(points=dxy, attrs=attrs))

    def _find_visible_interior_point(self, coordinates) -> Point | None:
        """
        Finds a point that's both inside the original (un-projected) polygon
        and projects into the visible plot bounds, or None if no such point
        could be found (e.g. this particular piece isn't actually visible in
        the current view). Used as known-interior ground truth by
        `_clip_wrapped_polygon`, to check that resolving a wrapped polygon's
        self-intersections didn't fill its outside instead of its inside.
        """
        original = ShapelyPolygon(coordinates)
        if not original.is_valid:
            original = original.buffer(0)
        if original.is_empty:
            return None

        minx, miny, maxx, maxy = original.bounds
        rng = np.random.default_rng(0)
        candidates = [original.representative_point()]
        candidates += [
            Point(x, y)
            for x, y in zip(rng.uniform(minx, maxx, 300), rng.uniform(miny, maxy, 300))
        ]

        for pt in candidates:
            if not original.contains(pt):
                continue

            x, y = self.tx.transform(pt.x, pt.y)
            if (
                np.isfinite(x)
                and np.isfinite(y)
                and self.minx <= x <= self.maxx
                and self.miny <= y <= self.maxy
            ):
                return Point(x, y)

        return None

    def _clip_wrapped_polygon(self, coordinates, px, py) -> list[ShapelyPolygon]:
        """
        Given an already-projected polygon ring that may span a projection's
        seam/pole, returns the ring(s) actually visible within the plot's
        bounds.

        A polygon crossing the seam projects into a ring with one or more
        edges that are straight chords connecting points which aren't really
        adjacent on the sphere (the projected line jumped or went non-finite
        between them -- see Canvas.line, which cuts a *line* at these same
        points). A polygon can't just stop at a cut, though; it needs to stay
        closed.

        The common case is a small, locally compact object that just happens
        to straddle the seam (e.g. a DSO catalog polygon near RA 0/360, or a
        pole singularity landing inside a small shape) -- there, each real
        boundary arc's own two cut ends stay close together, so closing an
        arc by connecting them directly with a short chord is a safe,
        unambiguous stand-in for "whatever the boundary does off-screen." No
        buffer(0)/winding involved, so there's nothing to resolve wrong.

        For a polygon that spans a large stretch of sky (the Milky Way, or
        any shape whose cut ends land far apart), a short chord isn't a
        reasonable stand-in, so this falls back to repairing the whole ring
        at once with buffer(0) and intersecting it with the plot's own
        bounds -- GEOS resolves that the same way regardless of which
        projection produced the ring.

        buffer(0)'s self-intersection repair has to pick a winding for the
        patched-up ring, though, and the "fake" edges bridging a jump/pole
        can just as easily land on the wrong side -- filling everywhere
        BUT the true shape instead of the shape itself. So the result is
        checked against a point known to be inside the original polygon, and
        swapped for its complement (within the visible bounds) if that check
        fails.

        Known limitation: that correction is a single global flip, checked
        against one point. A ring with more than one jump (e.g. a polygon
        that fully encircles the sky, crossing the seam twice) gets a fake
        chord at *each* jump, and buffer(0) picks a winding per
        self-intersection independently -- one chord can resolve correctly
        while another resolves inverted in the same ring, which this can't
        detect or fix (checking more points wouldn't help, since the two bad
        regions can each look "correct" from a single sample). Confirmed
        correct for single-jump cases; a wrap that still looks inside-out
        after this likely needs real polygon clipping (walking each real
        boundary arc and closing gaps via the view box's own corners)
        instead of this repair-and-check approach.
        """
        finite = np.isfinite(px) & np.isfinite(py)

        if finite.all():
            jumps = np.hypot(np.diff(px), np.diff(py)) > self._max_projection_jump
            if not jumps.any():
                return [ShapelyPolygon(zip(px, py))]

        view = box(self.minx, self.miny, self.maxx, self.maxy)
        arcs = _geometry.split_ring_at_projection_jumps(
            list(zip(px, py)), max_jump=self._max_projection_jump
        )
        if arcs and all(
            math.hypot(arc[-1][0] - arc[0][0], arc[-1][1] - arc[0][1])
            <= 0.1 * self._max_projection_jump
            for arc in arcs
        ):
            pieces = []
            for arc in arcs:
                if len(arc) < 3:
                    continue
                local = ShapelyPolygon([*arc, arc[0]])
                if not local.is_valid:
                    local = local.buffer(0)
                clipped = local.intersection(view)
                if not clipped.is_empty:
                    pieces.extend(
                        clipped.geoms if hasattr(clipped, "geoms") else [clipped]
                    )
            return [g for g in pieces if g.geom_type == "Polygon"]

        # non-finite coords (e.g. a projection's pole) can't be represented
        # in a shapely geometry -- push them far outside the plot's bounds
        # instead, so they still resolve to "outside the visible area" below.
        far = 1e6 * max(self.maxx - self.minx, self.maxy - self.miny)
        px = np.nan_to_num(px, nan=far, posinf=far, neginf=-far)
        py = np.nan_to_num(py, nan=far, posinf=far, neginf=-far)

        raw = ShapelyPolygon(zip(px, py)).buffer(0)
        resolved = raw.intersection(view)

        inside_point = self._find_visible_interior_point(coordinates)
        if inside_point is not None and not resolved.contains(inside_point):
            resolved = view.difference(raw)

        if resolved.is_empty:
            return []
        if resolved.geom_type == "Polygon":
            return [resolved]

        return [g for g in resolved.geoms if g.geom_type == "Polygon"]

    def polygon(
        self,
        coordinates: list[tuple[float, float]],
        style: PolygonStyle,
        cs: CoordinateSystem = CoordinateSystem.DATA,
        attrs: dict | None = None,
    ) -> None:
        # Antimeridian/seam wraparound only means something for raw ra/dec
        # (DATA) coordinates. For already-projected/pixel-space coordinates
        # (e.g. PROJECTED or DISPLAY, as used for arrows/debug overlays),
        # clipping at the projection's seam is meaningless and corrupts the
        # shape.
        if self.projection.wraps and cs == CoordinateSystem.DATA:
            arr = np.array(coordinates)
            px, py = self.tx.transform(arr[:, 0], arr[:, 1])
            polygons_split = self._clip_wrapped_polygon(coordinates, px, py)
            result_cs = CoordinateSystem.PROJECTED
        else:
            polygons_split = [ShapelyPolygon(coordinates)]
            result_cs = cs

        for p in polygons_split:
            if p.is_empty:
                continue

            polygon_coords = list(zip(*p.exterior.coords.xy))
            arr = np.array(polygon_coords)
            xs, ys = arr[:, 0], arr[:, 1]
            dx, dy = self._to_display(xs, ys, result_cs)
            dxy = list(zip(dx, dy))

            attrs = attrs or {}
            _attrs = {**style.css(self.scale), **attrs}

            if isinstance(style.fill, list):
                _attrs["fill"] = self._get_or_create_gradient(
                    stops=style.fill,
                    type=style.gradient_type,
                )

            self._add_element(style.zorder, Polygon(points=dxy, attrs=_attrs))

    def text(
        self,
        x: float,
        y: float,
        value: str,
        style: LabelStyle,
        angle: float = 0,
        cs: CoordinateSystem = CoordinateSystem.DATA,
        attrs: dict | None = None,
    ) -> None:
        """Plots text, with an optional rotation angle."""

        dx, dy = self._to_display(x, y, cs)

        attrs = attrs or {}
        _attrs = {**style.css(self.scale), **attrs}

        if angle:
            _attrs["transform"] = f"rotate({angle}, {dx}, {dy})"

        self._add_element(style.zorder, Text(x=dx, y=dy, attrs=_attrs, text=value))

    def title(
        self,
        value: str,
        style: LabelStyle,
    ) -> None:
        _attrs = {
            **style.css(self.scale),
            "text-anchor": "middle",
            # "dominant-baseline": "central",
        }
        self.layout.title = Region(
            elements=[
                (
                    style.zorder,
                    Text(
                        x=self.layout.axes.width / 2,
                        y=style.font_size * self.scale - style.padding_bottom,
                        attrs=_attrs,
                        text=value,
                    ),
                )
            ],
            height=style.font_size * self.scale + style.padding_bottom,
            width=self.layout.axes.width,
        )

    def legend(
        self,
        sections: list[tuple[str, dict]],
        style: LegendStyle,
        gid: str = "legend",
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
                h, w, _ = fonts.get_text_hw(
                    text=title,
                    font_name=style.title.font_name,
                    font_size=style.title.font_size * self.scale,
                    font_weight=style.title.font_weight,
                    italic=style.title.font_style == "italic",
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

                h, w, _ = fonts.get_text_hw(
                    text=label,
                    font_name=style.labels.font_name,
                    font_size=style.labels.font_size * self.scale,
                    font_weight=style.labels.font_weight,
                    italic=style.labels.font_style == "italic",
                )
                height += max(marker_size * self.scale, h) + style.label_padding
                w += (
                    marker_size * self.scale
                    + style.symbol_padding
                    + style.padding_x * 2
                )

                width = max(width, w)

                y += h + style.label_padding

            if i < len(sections) - 1:
                height += style.label_padding  # * 2.5
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
                (
                    1,
                    Group(
                        id=gid,
                        children=[
                            background_element,
                            *sections_elements,
                        ],
                    ),
                )
            ],
            height=height,
            width=width,
            location=style.location,
            margin_x=style.margin_x,
            margin_y=style.margin_y,
        )

    def table(
        self,
        headers: list[str],
        rows: list[list],
        style: TableStyle = None,
        padding_x: float = 28,
        padding_y: float = 20,
    ) -> None:
        """
        Plots a table of data with headers.

        The canvas only supports a single table (similar to the legend), so calling
        this again replaces the previous table instead of adding another one.

        Args:
            headers: List of column header labels
            rows: List of rows, where each row is a list of cell values (same length as `headers`). Values are converted to strings.
            style: Style for the table (header/cell text, border, and top padding). Defaults to a `TableStyle` with sensible defaults.
            padding_x: Horizontal padding within each cell, in pixels
            padding_y: Vertical padding within each cell, in pixels
        """
        style = style or TableStyle()
        header_style = style.header
        cell_style = style.cell
        border_style = style.border
        top = style.padding_top

        scale = self.scale
        header_attrs = header_style.css(scale)
        cell_attrs = cell_style.css(scale)
        border_attrs = border_style.css(scale)

        num_cols = len(headers)

        def cell_width(value, style: LabelStyle) -> float:
            _, w, _ = fonts.get_text_hw(
                text=str(value),
                font_name=style.font_name,
                font_size=style.font_size * scale,
                font_weight=style.font_weight,
                italic=style.font_style == "italic",
            )
            return w

        col_widths = [
            max(
                cell_width(headers[col], header_style),
                *[cell_width(row[col], cell_style) for row in rows],
            )
            + padding_x * 2
            for col in range(num_cols)
        ]

        header_height = header_style.font_size * scale + padding_y * 2
        row_height = cell_style.font_size * scale + padding_y * 2
        table_width = sum(col_widths)
        table_height = header_height + row_height * len(rows)

        def cell_text(value, x: float, row_top: float, row_height: float, style, attrs):
            y = row_top + row_height / 2 + style.font_size * scale / 2.75
            return Text(x=x, y=y, text=str(value), attrs=attrs)

        elements = []

        x = 0
        for col in range(num_cols):
            elements.append(
                (
                    1,
                    cell_text(
                        headers[col],
                        x + padding_x,
                        top,
                        header_height,
                        header_style,
                        header_attrs,
                    ),
                )
            )
            if col > 0:
                elements.append(
                    (
                        0,
                        Line(
                            x1=x,
                            y1=top,
                            x2=x,
                            y2=top + table_height,
                            attrs=border_attrs,
                        ),
                    )
                )
            x += col_widths[col]

        elements.append(
            (
                0,
                Line(
                    x1=0,
                    y1=top + header_height,
                    x2=table_width,
                    y2=top + header_height,
                    attrs=border_attrs,
                ),
            )
        )

        y = header_height
        for row in rows:
            x = 0
            for col in range(num_cols):
                elements.append(
                    (
                        1,
                        cell_text(
                            row[col],
                            x + padding_x,
                            top + y,
                            row_height,
                            cell_style,
                            cell_attrs,
                        ),
                    )
                )
                x += col_widths[col]
            y += row_height
            if y < table_height:
                elements.append(
                    (
                        0,
                        Line(
                            x1=0,
                            y1=top + y,
                            x2=table_width,
                            y2=top + y,
                            attrs=border_attrs,
                        ),
                    )
                )

        elements.append(
            (
                0,
                Rectangle(
                    x=0,
                    y=top,
                    width=table_width,
                    height=table_height,
                    attrs=border_attrs,
                ),
            )
        )

        self.layout.table = TableRegion(
            elements=elements,
            height=top + table_height,
            width=table_width,
            alignment=style.alignment,
        )

    def _axes_frame(
        self,
        style: PathStyle,
        labels: list | None = None,
        width_from_labels: bool = False,
        label_gid: str = "border-labels",
    ) -> None:
        """
        Creates the axes_frame region: a border drawn just outside the axes clip path,
        optionally with labels along it (e.g. gridline labels).

        Args:
            style: Style of border line
            labels: List of 2-tuples where the first item is a list of coordinates for a line that intersects the border,
                    and the second item is a string label for that intersection.
            label_gid: If given, the label elements are wrapped in a `<g id=label_gid>` instead of being added individually.

        """
        label_elements = []
        label_height = style.label.font_size * self.scale

        def text_width(text, font_size):
            _, w, _ = fonts.get_text_hw(
                text=text,
                font_name=style.label.font_name,
                font_size=font_size,
                font_weight=style.label.font_weight,
                italic=style.label.font_style == "italic",
            )
            return w

        if width_from_labels:
            text_widths = [
                text_width(label, style.label.font_size * self.scale)
                for _, label, _ in labels
                if label
            ]
            border_width = (
                max(text_widths) if text_widths else style.line.width * self.scale
            )
        else:
            border_width = style.line.width * self.scale

        # buffer is width / 2 because line is drawn at center of coordinates
        # in other words, half of the width is on the inside and half the width on outside of coordinates
        #
        # also offset by axes_border_offset so this frame begins exactly where
        # axes_border ends, rather than overlapping it
        border = self.clip_path_display.buffer(
            self._axes_border_offset + border_width / 2, join_style="mitre"
        )

        cx1, cy1, cx2, cy2 = self.clip_path_display.bounds

        # TODO : remove these offset vars? dont need cause of layout engine
        xoff = 0
        yoff = 0
        coords = list(zip(*border.exterior.coords.xy))
        border_line = LineString(coords)
        attrs = style.line.css(self.scale)

        if self.debug:
            clip_path = _translate_shape(self.clip_path_display, xoff=xoff, yoff=yoff)
            label_elements.append(
                (
                    10_000_000_000,
                    Polyline(
                        points=list(zip(*clip_path.exterior.coords.xy)),
                        attrs=LineStyle(stroke="red", width=4, zorder=1_000_000).css(
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
                        attrs=LineStyle(
                            stroke="#1effff", width=2, zorder=1_000_000
                        ).css(self.scale),
                    ),
                )
            )

        if labels:
            # 1. convert coordinates to display
            # 2. find intersection of line with border
            # 3. add text element at intersection

            for xy, text, locations in labels:
                if not text:
                    continue
                arr = np.array(xy)
                xs, ys = arr[:, 0], arr[:, 1]
                dx, dy = self._to_display(xs, ys)
                dxy = list(zip(dx, dy))
                dxy = [(x + xoff, y + yoff) for x, y in dxy]
                dxy = _geometry.extend_line(dxy, distance=border_width * 2)

                labeled_line = LineString(dxy)
                label_width = text_width(text, style.label.font_size * self.scale)

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
                    if locations and any(
                        (
                            ix.y - label_height / 2 < cy1 + yoff
                            and "top" not in locations,
                            ix.y + label_height / 2 > cy2 + yoff
                            and "bottom" not in locations,
                            ix.x - label_width / 2 < cx1 + xoff
                            and "left" not in locations,
                            ix.x + label_width / 2 > cx2 + xoff
                            and "right" not in locations,
                        )
                    ):
                        continue

                    element = Text(
                        x=ix.x,
                        y=ix.y + style.label.font_size * self.scale / 2.75,
                        text=text,
                        attrs={
                            **style.label.css(self.scale),
                            "text-anchor": "middle",
                            # "dominant-baseline": "central", # not supported in cairo svg
                        },
                    )
                    label_elements.append((style.line.zorder + 10, element))

        border = self.clip_path_display.buffer(
            self._axes_border_offset + border_width, join_style="mitre"
        )
        bx1, by1, bx2, by2 = border.bounds

        elements = [(style.line.zorder, Polyline(points=coords, attrs=attrs))]
        if label_elements:
            label_zorder = max(z for z, _ in label_elements)
            elements.append(
                (
                    label_zorder,
                    Group(id=label_gid, children=[e for _, e in label_elements]),
                )
            )

        self.layout.axes_frame = Region(
            elements=elements,
            height=(by2 - by1),
            width=(bx2 - bx1),
        )

    def render(self, text_as_path: bool = False) -> str:
        """Renders the canvas to an SVG string"""
        return self.layout.render(self.style, text_as_path, self.scale)

    def export(
        self, filename: str | Path, text_as_path: bool = False, scale: float = 1
    ) -> None:
        """
        Exports the SVG to an SVG or PNG file. Type is inferred by filename.
        """
        _filename = str(filename)

        if _filename.endswith("png"):
            png.export_png_cairo(
                filename=_filename,
                svg_source=self.render(text_as_path=True),
                scale=scale,
            )
            # png.export_png_resvg(
            #     filename=filename, svg_source=self.render(text_as_path=True)
            # )
            return

        with open(_filename, "w", buffering=1024 * 1024) as outfile:
            outfile.write(self.render(text_as_path=text_as_path))
