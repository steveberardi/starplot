import math
from typing import Callable
from functools import cache

from shapely import Polygon
from skyfield.api import wgs84

from starplot.coordinates import CoordinateSystem
from starplot import geometry
from starplot.mixins import ExtentMaskMixin
from starplot.models.observer import Observer
from starplot.plotters import (
    ConstellationPlotterMixinSVG,
    MilkyWayPlotterMixin,
    LegendPlotterMixin,
    GradientBackgroundMixin,
    ArrowPlotterMixinSVG,
)

# from starplot.plotters.text import CollisionHandler
from starplot.projections import StereoNorth, StereoSouth, ProjectionBase
from starplot.styles import (
    ObjectStyle,
    PlotStyle,
    PathStyle,
    GradientDirection,
    extensions,
)
from starplot.profile import profile
from starplot.styles.helpers import use_style
from starplot.svg.base import BasePlot
from starplot.svg.dsos import DsoPlotterMixin
from starplot.svg.text import TextPlotterMixin, CollisionHandler


class MapPlot(
    BasePlot,
    ExtentMaskMixin,
    DsoPlotterMixin,
    MilkyWayPlotterMixin,
    TextPlotterMixin,
    ConstellationPlotterMixinSVG,
    ArrowPlotterMixinSVG,
    # LegendPlotterMixin,
    # GradientBackgroundMixin,
):
    """Creates a new map plot.

    Args:
        projection: [Projection](/reference-mapplot/#projections) of the map
        ra_min: Minimum right ascension of the map's extent, in degrees (0...360)
        ra_max: Maximum right ascension of the map's extent, in degrees (0...360)
        dec_min: Minimum declination of the map's extent, in degrees (-90...90)
        dec_max: Maximum declination of the map's extent, in degrees (-90...90)
        observer: Observer instance which specifies a time and place. Defaults to an observer at epoch J2000
        ephemeris: Ephemeris to use for calculating planet positions (see [Skyfield's documentation](https://rhodesmill.org/skyfield/planets.html) for details)
        style: Styling for the plot (colors, sizes, fonts, etc). If `None`, it defaults to `PlotStyle()`
        resolution: Size (in pixels) of largest dimension of the map
        point_label_handler: Default [CollisionHandler][starplot.CollisionHandler] for point labels.
        area_label_handler: Default [CollisionHandler][starplot.CollisionHandler] for area labels.
        path_label_handler: Default [CollisionHandler][starplot.CollisionHandler] for path labels.
        clip_path: An optional Shapely Polygon that specifies the clip path of the plot -- only objects inside the polygon will be plotted. If `None` (the default), then the clip path will be the extent of the map you specified with the RA/DEC parameters.
        scale: Scaling factor that will be applied to all sizes in styles (e.g. font size, marker size, line widths, etc). For example, if you want to make everything 2x bigger, then set the scale to 2. At `scale=1` and `resolution=4096` (the default), all sizes are optimized visually for a map that covers 1-3 constellations. So, if you're creating a plot of a _larger_ extent, then it'd probably be good to decrease the scale (i.e. make everything smaller) -- and _increase_ the scale if you're plotting a very small area.
        autoscale: If True, then the scale will be set automatically based on resolution.
        suppress_warnings: If True (the default), then all warnings will be suppressed

    Returns:
        MapPlot: A new instance of a MapPlot

    """

    def __init__(
        self,
        projection: ProjectionBase,
        ra_min: float = 0,
        ra_max: float = 360,
        dec_min: float = -90,
        dec_max: float = 90,
        observer: Observer = None,
        ephemeris: str = "de440s.bsp",
        style: PlotStyle = None,
        resolution: int = 4096,
        point_label_handler: CollisionHandler = None,
        area_label_handler: CollisionHandler = None,
        path_label_handler: CollisionHandler = None,
        clip_path: Polygon = None,
        scale: float = 1.0,
        autoscale: bool = False,
        suppress_warnings: bool = True,
        *args,
        **kwargs,
    ) -> "MapPlot":
        observer = observer or Observer.at_epoch(2000)
        style = style or PlotStyle().extend(extensions.MAP)

        if ra_min > ra_max:
            raise ValueError("ra_min must be less than ra_max")
        if dec_min > dec_max:
            raise ValueError("dec_min must be less than dec_max")
        if dec_min < -90 or dec_max > 90:
            raise ValueError("Declination out of range (must be -90...90)")

        self.ra_min = ra_min
        self.ra_max = ra_max
        self.dec_min = dec_min
        self.dec_max = dec_max

        bounds = [
            self.ra_min,
            self.dec_min,
            self.ra_max,
            self.dec_max,
        ]

        super().__init__(
            observer,
            ephemeris,
            style,
            resolution,
            point_label_handler=point_label_handler,
            area_label_handler=area_label_handler,
            path_label_handler=path_label_handler,
            scale=scale,
            autoscale=autoscale,
            suppress_warnings=suppress_warnings,
            projection=projection,
            bounds=bounds,
            invert_x=False,
            invert_y=False,
            clip_path=clip_path,
            *args,
            **kwargs,
        )

        self.logger.debug("Creating MapPlot...")

        self._adjust_radec_minmax()

    @cache
    def in_bounds(self, ra: float, dec: float) -> bool:
        """Determine if a coordinate is within the bounds of the plot.

        Args:
            ra: Right ascension, in degrees (0...360)
            dec: Declination, in degrees (-90...90)

        Returns:
            True if the coordinate is in bounds, otherwise False
        """
        x_axes, y_axes = self.canvas._to_axes(ra, dec)
        return 0 <= x_axes <= 1 and 0 <= y_axes <= 1

    def _in_bounds_xy(self, x: float, y: float) -> bool:
        return self.in_bounds(x, y)

    def _latlon_bounds(self):
        # convert the RA/DEC bounds to lat/lon bounds
        return [
            -1 * self.ra_min,
            -1 * self.ra_max,
            self.dec_min,
            self.dec_max,
        ]

    def _adjust_radec_minmax(self):
        if self._is_global_extent():
            return

        minx, self.dec_min, maxx, self.dec_max = self.canvas.bounds

        if minx < 0 or maxx < 0:
            minx += 360
            maxx += 360

        # adjust the X min/max if the Y bounds is near the poles
        if (isinstance(self.projection, (StereoNorth, StereoSouth))) and (
            self.dec_max > 80 or self.dec_min < -80
        ):
            self.ra_min = 0
            self.ra_max = 360

        else:
            self.ra_min = minx
            self.ra_max = maxx

        self.logger.debug(
            f"Extent = RA ({self.ra_min:.2f}, {self.ra_max:.2f}) DEC ({self.dec_min:.2f}, {self.dec_max:.2f})"
        )

    @use_style(ObjectStyle, "zenith")
    def zenith(
        self,
        style: ObjectStyle = None,
        label: str = None,
        legend_label: str = "Zenith",
    ):
        """
        Plots a marker for the zenith (requires `lat`, `lon`, and `dt` to be defined when creating the plot)

        Args:
            style: Style of the zenith marker. If None, then the plot's style definition will be used.
            label: Label for the zenith
            legend_label: Label in the legend
        """
        if self.observer is None:
            raise ValueError("observer is required for plotting the zenith")

        geographic = wgs84.latlon(
            latitude_degrees=self.observer.lat, longitude_degrees=self.observer.lon
        )
        observer = geographic.at(self.observer.timescale)
        zenith = observer.from_altaz(alt_degrees=90, az_degrees=0)
        ra, dec, _ = zenith.radec()

        self.marker(
            ra=ra.hours * 15,
            dec=dec.degrees,
            style=style,
            label=label,
            legend_label=legend_label,
        )

    @use_style(PathStyle, "horizon")
    def horizon(
        self,
        style: PathStyle = None,
        labels: list = ["N", "E", "S", "W"],
    ):
        """
        Draws a [great circle](https://en.wikipedia.org/wiki/Great_circle) representing the horizon for the given `lat`, `lon` at time `dt` (so you must define these when creating the plot to use this function)

        Args:
            style: Style of the horizon path. If None, then the plot's style definition will be used.
            labels: List of labels for cardinal directions. **NOTE: labels should be in the order: North, East, South, West.**
        """
        if self.observer is None:
            raise ValueError("observer is required for plotting the horizon")

        geographic = wgs84.latlon(
            latitude_degrees=self.observer.lat, longitude_degrees=self.observer.lon
        )
        observer = geographic.at(self.observer.timescale)
        zenith = observer.from_altaz(alt_degrees=90, az_degrees=0)
        ra, dec, _ = zenith.radec()

        polygon = geometry.ellipse(
            center=(ra.hours * 15, dec.degrees),
            height_degrees=180,
            width_degrees=180,
            num_pts=100,
        )
        points = list(zip(*polygon.exterior.coords.xy))
        x = []
        y = []

        for ra, dec in points:
            x0, y0 = self._prepare_coords(ra, dec)
            x.append(x0)
            y.append(y0)

        style_kwargs = {}
        style_kwargs["clip_on"] = True
        style_kwargs["clip_path"] = self._background_clip_path
        self.ax.plot(
            x,
            y,
            dash_capstyle=style.line.dash_capstyle,
            **style.line.matplot_kwargs(self.scale),
            **style_kwargs,
            **self._plot_kwargs(),
        )

        if not labels:
            return

        north = observer.from_altaz(alt_degrees=0, az_degrees=0)
        east = observer.from_altaz(alt_degrees=0, az_degrees=90)
        south = observer.from_altaz(alt_degrees=0, az_degrees=180)
        west = observer.from_altaz(alt_degrees=0, az_degrees=270)

        cardinal_directions = [north, east, south, west]

        text_kwargs = dict(
            **style.label.matplot_kwargs(self.scale),
            xytext=(
                style.label.offset_x * self.scale,
                style.label.offset_y * self.scale,
            ),
            textcoords="offset points",
            path_effects=[],
            clip_on=True,
        )

        for i, position in enumerate(cardinal_directions):
            ra, dec, _ = position.radec()
            x, y = self._prepare_coords(ra.hours * 15, dec.degrees)
            self._text(x, y, labels[i], **text_kwargs)

    @profile
    @use_style(PathStyle, "gridlines")
    def gridlines(
        self,
        style: PathStyle = None,
        labels: bool = True,
        ra_locations: list[float] = None,
        dec_locations: list[float] = None,
        ra_formatter_fn: Callable[[float], str] = None,
        dec_formatter_fn: Callable[[float], str] = None,
        tick_marks: bool = False,
        ra_tick_locations: list[float] = None,
        dec_tick_locations: list[float] = None,
    ):
        """Plots gridlines

        Args:
            style: Styling of the gridlines. If None, then the plot's style (specified when creating the plot) will be used
            labels: If True, then labels for each gridline will be plotted on the outside of the axes.
            ra_locations: List of Right Ascension locations for the gridlines (in degrees, 0...360). Defaults to every 15 degrees.
            dec_locations: List of Declination locations for the gridlines (in degrees, -90...90). Defaults to every 10 degrees.
            ra_formatter_fn: Callable for creating labels of right ascension gridlines
            dec_formatter_fn: Callable for creating labels of declination gridlines
            tick_marks: If True, then tick marks will be plotted outside the axis. **Only supported for rectangular projections (e.g. Mercator, Miller)**
            ra_tick_locations: List of Right Ascension locations for the tick marks (in degrees, 0...260)
            dec_tick_locations: List of Declination locations for the tick marks (in degrees, -90...90)
        """

        ra_formatter_fn_default = lambda r: f"{math.floor(r)}h"  # noqa: E731
        dec_formatter_fn_default = lambda d: f"{round(d)}\u00b0 "  # noqa: E731

        ra_formatter_fn = ra_formatter_fn or ra_formatter_fn_default
        dec_formatter_fn = dec_formatter_fn or dec_formatter_fn_default

        # def ra_formatter(x, pos) -> str:
        #     ra = lon_to_ra(x)
        #     return ra_formatter_fn(ra)

        # def dec_formatter(x, pos) -> str:
        #     return dec_formatter_fn(x)

        ra_locations = ra_locations or [
            x for x in range(0, 360, 15)  # if self.ra_min <= x <= self.ra_max
        ]
        dec_locations = dec_locations or [
            y for y in range(-80, 90, 10)  # if self.dec_min <= y <= self.dec_max
        ]

        for ra in ra_locations:
            coords = geometry.line_segment((ra, self.dec_min), (ra, self.dec_max), 0.5)
            self.line(
                coordinates=coords,
                style=style,
            )

        for dec in dec_locations:
            coords = geometry.line_segment((0.00001, dec), (359.99999, dec), 0.5)
            self.line(
                coordinates=coords,
                style=style,
            )

        # TODO : labels, tick marks

        return
