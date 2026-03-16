import logging

import numpy as np
from shapely import Polygon, LineString

from pyproj import CRS, Transformer

from starplot.coordinates import CoordinateSystem
from starplot import models, warnings
from starplot import geometry as _geometry
from starplot.config import settings as StarplotSettings, SvgTextType
from starplot.styles import (
    PlotStyle,
    MarkerStyle,
    ObjectStyle,
    LabelStyle,
    MarkerSymbolEnum,
    PathStyle,
    PolygonStyle,
    GradientDirection,
    AnchorPointEnum,
)
from starplot.projections import ProjectionBase
from starplot.svg import symbols

LOGGER = logging.getLogger("starplot-svg")
LOG_HANDLER = logging.StreamHandler()
LOG_FORMATTER = logging.Formatter(
    "\033[1;34m%(name)s\033[0m:[%(levelname)s]: %(message)s"
)
LOG_HANDLER.setFormatter(LOG_FORMATTER)
LOGGER.addHandler(LOG_HANDLER)


CRS_WNU = CRS.from_proj4("+proj=latlon +ellps=sphere +axis=wnu +a=6378137")


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

    precision: int = 4

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
        precision: int = 4,
        *args,
        **kwargs,
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

        self.log_level = logging.DEBUG if self.debug else logging.ERROR
        self.logger = LOGGER
        self.logger.setLevel(self.log_level)

        self._init_bounds()

    def _to_axes(self, x, y):
        px, py = self.tx.transform(x, y)
        return normalize(px, self.minx, self.maxx), normalize(py, self.miny, self.maxy)

    def _to_display(self, x, y):
        ax, ay = self._to_axes(x, y)
        x = ax * self.width
        y = (1 - ay) * self.height
        if self.precision == 0:
            return x.astype(int), y.astype(int)
        return np.round(x, self.precision), np.round(y, self.precision)

    def _init_bounds(self):
        self.projected_bounds = self.tx.transform_bounds(*self.bounds)
        self.minx, self.miny, self.maxx, self.maxy = self.projected_bounds
        left, bottom, right, top = self.projected_bounds

        span_x = abs(right - left)
        span_y = abs(top - bottom)

        if span_x > span_y:
            ratio = span_x / span_y
            self.width = self.resolution
            self.height = self.width / ratio
        else:
            ratio = span_y / span_x
            self.height = self.resolution
            self.width = self.height / ratio

        self.logger.debug(f"Size = {self.height} x {self.width}")

    def _register_symbol(self, symbol_id: str, value: str):
        if symbol_id in self.symbol_ids:
            return
        self.symbols.add(value)
        self.symbol_ids.add(symbol_id)

    def marker(self, x, y, style: MarkerStyle) -> None:
        dx, dy = self._to_display(x, y)

        symbol_id, value = symbols.get(style)
        self._register_symbol(symbol_id, value)

        # this can be bottleneck, need to cache
        css = " ".join([f'{k}="{v}"' for k, v in style.css().items()])

        self.elements.append(
            (style.zorder, symbols.use(symbol_id, dx, dy, style.size, style.size, css))
        )

    def markers(self, x, y, style: MarkerStyle) -> None:
        dx, dy = self._to_display(x, y)

        symbol_id, value = symbols.get(style)
        self._register_symbol(symbol_id, value)

        # this can be bottleneck, need to cache
        css = " ".join([f'{k}="{v}"' for k, v in style.css().items()])

        for x, y in list(zip(dx, dy)):
            self.elements.append(
                (
                    style.zorder,
                    symbols.use(symbol_id, x, y, style.size, style.size, css),
                )
            )

    def line(
        self,
        coordinates: list[tuple[float, float]] = None,
        style: PathStyle = None,
        label: str = None,
        num_labels: int = 2,
    ) -> None:
        arr = np.array(coordinates)
        xs, ys = arr[:, 0], arr[:, 1]
        dx, dy = self._to_display(xs, ys)
        dxy = list(zip(dx, dy))

        points = " ".join([f"{x},{y}" for x, y in dxy])

        attrs = " ".join([f'{k}="{v}"' for k, v in style.line.css().items()])

        self.elements.append(
            (style.line.zorder, f'<polyline points="{points}" {attrs} />')
        )

    def polygon(
        self, coordinates: list[tuple[float, float]], style: PolygonStyle
    ) -> float:
        arr = np.array(coordinates)
        xs, ys = arr[:, 0], arr[:, 1]
        dx, dy = self._to_display(xs, ys)
        dxy = list(zip(dx, dy))

        points = " ".join([f"{x},{y}" for x, y in dxy])

        attrs = " ".join([f'{k}="{v}"' for k, v in style.css().items()])

        self.elements.append((style.zorder, f'<polygon points="{points}" {attrs} />'))

    def ellipse(self) -> float:
        ...

    # @abstractmethod
    # def text(self) -> float:
    #     ...

    # @abstractmethod
    # def gridlines(self) -> float:
    #     ...

    # @abstractmethod
    # def legend(self) -> float:
    #     ...

    def export(self, filename):
        with open(filename, "w", buffering=1024 * 1024) as outfile:
            outfile.write(
                f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.width}" height="{self.height}" viewBox="0 0 {self.width} {self.height}">'
            )

            if self.symbols:
                outfile.write("\n\n<defs>\n")
                for symbol in self.symbols:
                    outfile.write(f"{symbol}\n")
                outfile.write("</defs>\n\n")

            sorted_by_z = sorted(self.elements, key=lambda e: e[0])
            for _, e in sorted_by_z:
                outfile.write(e + "\n")

            outfile.write("</svg>")
