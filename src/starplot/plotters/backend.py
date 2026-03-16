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
        scale: float = 1.0,
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
        self.scale = scale

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
        suppress_warnings: bool = True,
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

        if StarplotSettings.svg_text_type == SvgTextType.PATH:
            plt.rcParams["svg.fonttype"] = "path"
        else:
            plt.rcParams["svg.fonttype"] = "none"

        if suppress_warnings:
            warnings.suppress()

        self._init_figure()

        fonts.load()

    def close(self) -> None:
        """Closes the underlying matplotlib figure."""
        if self.fig:
            plt.close(self.fig)

    def export(self, filename: str, padding: float = 0, **kwargs):
        """Exports the plot to an image file.

        Args:
            filename: Filename of exported file (the format will be inferred from the extension)
            padding: Padding (in inches) around the image
            **kwargs: Any keyword arguments to pass through to matplotlib's `savefig` method

        """
        self.fig.savefig(
            filename,
            bbox_inches="tight",
            pad_inches=padding * self.scale,
            dpi=DPI,
            **kwargs,
        )

    def title(self, text: str, style: LabelStyle = None):
        """
        Plots a title at the top of the plot

        Args:
            text: Title text to plot
            style: Styling of the title. If None, then the plot's style (specified when creating the plot) will be used
        """
        style_kwargs = style.matplot_kwargs(self.scale)
        style_kwargs.pop("linespacing", None)
        style_kwargs["pad"] = style.line_spacing
        self.ax.set_title(text, **style_kwargs)

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
