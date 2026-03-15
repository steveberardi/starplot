from abc import ABC, abstractmethod

import numpy as np
from matplotlib import patches
from matplotlib import pyplot as plt, patheffects
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from shapely import Polygon, LineString

from starplot.coordinates import CoordinateSystem
from starplot import models, warnings
from starplot import geometry as _geometry
from starplot.config import settings as StarplotSettings, SvgTextType
from starplot.data import load, ecliptic
from starplot.data.translations import translate
from starplot.models.planet import PlanetName, PLANET_LABELS_DEFAULT
from starplot.models.moon import MoonPhase
from starplot.models.optics import Optic, Camera
from starplot.models.observer import Observer
from starplot.styles import (
    PlotStyle,
    MarkerStyle,
    ObjectStyle,
    LabelStyle,
    MarkerSymbolEnum,
    PathStyle,
    PolygonStyle,
    GradientDirection,
    fonts,
    AnchorPointEnum,
)
from starplot.projections import ProjectionBase

DPI = 100


class Canvas(ABC):
    resolution: int

    projection: ProjectionBase

    bounds: tuple[float, float, float, float]

    style: PlotStyle

    invert_x: bool = False
    invert_y: bool = False

    def __init__(
        self,
        resolution: int,
        projection: ProjectionBase,
        bounds: tuple[float, float, float, float],
        style: PlotStyle,
        clip_path=None,
        invert_x: bool = False,
        invert_y: bool = False,
        *args,
        **kwargs,
    ):
        self.resolution = resolution
        self.projection = projection
        self.bounds = bounds
        self.style = style

        self.clip_path = clip_path
        
        self.invert_x = invert_x
        self.invert_y = invert_y


    @abstractmethod
    def marker(self) -> float:
        ...

    @abstractmethod
    def line(self) -> float:
        ...

    @abstractmethod
    def ellipse(self) -> float:
        ...

    @abstractmethod
    def polygon(self) -> float:
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


class MplCanvas(Canvas):
    _background_clip_path = None
    _clip_path_polygon: Polygon = None  # clip path in display coordinates
    _gradient_direction: GradientDirection = GradientDirection.LINEAR

    ax: Axes
    """
    The underlying [Matplotlib axes](https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.html#matplotlib.axes.Axes) that everything is plotted on.
    
    **Important**: Most Starplot plotting functions also specify a transform based on the plot's projection when plotting things on the Matplotlib Axes instance, so use this property at your own risk!
    """

    fig: Figure
    """
    The underlying [Matplotlib figure](https://matplotlib.org/stable/api/_as_gen/matplotlib.figure.Figure.html#matplotlib.figure.Figure) that the axes is drawn on.
    """

    def __init__(
        self,
        resolution: int,
        projection: ProjectionBase,
        bounds: tuple[float, float, float, float],
        style: PlotStyle,
        *args,
        **kwargs,
    ):
        super().__init__(
            resolution=resolution,
            projection=projection,
            bounds=bounds,
            style=style,
            *args,
            **kwargs,
        )

        self._init_figure()

    def _fit_to_ax(self) -> None:
        self.fig.draw_without_rendering()
        bbox = self.ax.get_window_extent().transformed(
            self.fig.dpi_scale_trans.inverted()
        )
        width, height = bbox.width, bbox.height
        self.fig.set_size_inches(width, height)

    def _set_extent(self):
        if self._is_global_extent():
            # this cartopy function works better for setting global extents
            self.ax.set_global()
        else:
            self.ax.set_extent(self.bounds, crs=self._plate_carree)

    def _init_figure(self):
        px = 1 / DPI  # pixel in inches
        self.pixels_per_point = DPI / 72
        self.dpi = DPI
        self.figure_size = self.resolution * px

        self.fig = plt.figure(
            figsize=(self.figure_size, self.figure_size),
            facecolor=self.style.figure_background_color.as_hex(),
            dpi=DPI,
        )

        self._proj = self.projection.crs
        self.ax = self.fig.add_subplot(1, 1, 1, projection=self._proj)
        self.fig.subplots_adjust(left=0, right=1, top=1, bottom=0)

        # self._set_extent()
        # self._adjust_radec_minmax()

        self._fit_to_ax()
        # self._plot_background_clip_path()
