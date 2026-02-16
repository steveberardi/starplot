from functools import cache
from typing import Callable

import numpy as np
import astropy.units as u
from astropy.coordinates import SkyCoord
from cartopy import crs as ccrs
from matplotlib import pyplot as plt, patches
from matplotlib.ticker import FixedLocator, FuncFormatter
from skyfield.api import Star as SkyfieldStar
from skyfield.framelib import galactic_frame

from starplot.coordinates import CoordinateSystem
from starplot.plots.base import BasePlot, DPI
from starplot.mixins import ExtentMaskMixin
from starplot.models.observer import Observer
from starplot.plotters import (
    ConstellationPlotterMixin,
    StarPlotterMixin,
    DsoPlotterMixin,
    MilkyWayPlotterMixin,
    GradientBackgroundMixin,
    LegendPlotterMixin,
    ArrowPlotterMixin,
)
from starplot.plotters.text import CollisionHandler
from starplot.styles import (
    PlotStyle,
    extensions,
    use_style,
    PathStyle,
    GradientDirection,
)


class GalaxyPlot(
    BasePlot,
    ExtentMaskMixin,
    ConstellationPlotterMixin,
    StarPlotterMixin,
    DsoPlotterMixin,
    MilkyWayPlotterMixin,
    LegendPlotterMixin,
    GradientBackgroundMixin,
    ArrowPlotterMixin,
):
    """Creates a new galaxy plot.

    Args:

        center_lon: Central galactic longitude of the Mollweide projection
        observer: Observer instance which specifies a time and place. Defaults to `Observer()`
        ephemeris: Ephemeris to use for calculating planet positions (see [Skyfield's documentation](https://rhodesmill.org/skyfield/planets.html) for details)
        style: Styling for the plot (colors, sizes, fonts, etc). If `None`, it defaults to `PlotStyle()`
        resolution: Size (in pixels) of largest dimension of the map
        collision_handler: Default [CollisionHandler][starplot.CollisionHandler] for the plot that describes what to do on label collisions with other labels, markers, etc.
        scale: Scaling factor that will be applied to all relevant sizes in styles (e.g. font size, marker size, line widths, etc). For example, if you want to make everything 2x bigger, then set scale to 2.
        autoscale: If True, then the scale will be automatically set based on resolution
        suppress_warnings: If True (the default), then all warnings will be suppressed

    Returns:
        GalaxyPlot: A new instance of a GalaxyPlot

    """

    _coordinate_system = CoordinateSystem.RA_DEC
    _gradient_direction = GradientDirection.MOLLWEIDE

    def __init__(
        self,
        center_lon: float = 0,
        observer: Observer = None,
        ephemeris: str = "de421.bsp",
        style: PlotStyle = None,
        resolution: int = 4096,
        collision_handler: CollisionHandler = None,
        scale: float = 1.0,
        autoscale: bool = False,
        suppress_warnings: bool = True,
        *args,
        **kwargs,
    ) -> "GalaxyPlot":
        observer = observer or Observer()
        style = style or PlotStyle().extend(extensions.MAP)

        super().__init__(
            observer,
            ephemeris,
            style,
            resolution,
            collision_handler=collision_handler,
            scale=scale,
            autoscale=autoscale,
            suppress_warnings=suppress_warnings,
            *args,
            **kwargs,
        )

        self.center_lon = center_lon
        self.logger.debug("Creating GalaxyPlot...")
        self._geodetic = ccrs.Geodetic()
        self._plate_carree = ccrs.PlateCarree()

        self._crs = ccrs.CRS(
            proj4_params=[
                ("proj", "latlong"),
                ("axis", "wnu"),  # invert
                ("a", "6378137"),
            ],
            globe=ccrs.Globe(ellipse="sphere", flattening=0),
        )

        self._init_plot()
        self._calc_position()

    def _prepare_coords(self, ra, dec) -> (float, float):
        """Converts RA/DEC to galactic coordinates (degrees)"""
        if ra > 360:
            ra -= 360
        if ra < 0:
            ra += 360
        point = SkyfieldStar(ra_hours=ra / 15, dec_degrees=dec)
        lat, lon, _ = self.observe(point).frame_latlon(galactic_frame)

        return lon.degrees, lat.degrees

    def _prepare_star_coords(self, df, limit_by_altaz=True):
        stars_position = self.observe(SkyfieldStar.from_dataframe(df))
        lat, lon, _ = stars_position.frame_latlon(galactic_frame)

        df["x"], df["y"] = (
            lon.degrees,
            lat.degrees,
        )
        return df

    def _plot_kwargs(self) -> dict:
        return dict(transform=self._crs)

    @cache
    def in_bounds(self, ra, dec) -> bool:
        """Determine if a coordinate is within the bounds of the plot.

        Args:
            ra: Right ascension, in hours (0...24)
            dec: Declination, in degrees (-90...90)

        Returns:
            True if the coordinate is in bounds, otherwise False
        """
        lon, lat = self._prepare_coords(ra, dec)
        return self.in_bounds_lonlat(lon, lat)

    def in_bounds_lonlat(self, lon, lat) -> bool:
        """Determine if a galactic coordinate is within the bounds of the plot.

        Args:
            lon: Galactic longitude in degrees (0...360)
            lat: Galactic latitude in degrees (-90...90)

        Returns:
            True if the coordinate is in bounds, otherwise False
        """
        x, y = self._proj.transform_point(lon, lat, self._crs)
        data_to_axes = self.ax.transData + self.ax.transAxes.inverted()
        x_axes, y_axes = data_to_axes.transform((x, y))
        return 0 <= x_axes <= 1 and 0 <= y_axes <= 1

    def _in_bounds_xy(self, x: float, y: float) -> bool:
        return self.in_bounds_lonlat(x, y)

    def _polygon(self, points, style, **kwargs):
        super()._polygon(points, style, transform=self._crs, **kwargs)

    def _calc_position(self):
        self.location = self.ephemeris["earth"]
        self.observe = self.location.at(self.observer.timescale).observe

        self.ra_min = 0
        self.ra_max = 360
        self.dec_min = -90
        self.dec_max = 90

        self.logger.debug(
            f"Extent = RA ({self.ra_min:.2f}, {self.ra_max:.2f}) DEC ({self.dec_min:.2f}, {self.dec_max:.2f})"
        )

    @use_style(PathStyle, "galactic_equator")
    def galactic_equator(
        self,
        style: PathStyle = None,
        label: str = "GALACTIC EQUATOR",
        collision_handler: CollisionHandler = None,
    ):
        """
        Plots the galactic equator

        Args:
            style: Styling of the galactic equator. If None, then the plot's style will be used
            label: How the galactic equator will be labeled on the plot
            collision_handler: An instance of [CollisionHandler][starplot.CollisionHandler] that describes what to do on label collisions with other labels, markers, etc. If `None`, then the collision handler of the plot will be used.
        """
        lons = np.array([ra for ra in range(0, 361)])  # galactic longitudes
        lats = np.array([0] * 361)  # galactic latitudes

        coords = SkyCoord(l=lons * u.deg, b=lats * u.deg, frame="galactic")
        coords_eq = coords.icrs

        ra_values = coords_eq.ra.degree
        dec_values = coords_eq.dec.degree

        radec = list(zip(ra_values, dec_values))

        self.line(
            style=style.line,
            coordinates=radec,
        )

        if not label:
            return

        label_spacing = int(len(radec) / 4)

        for ra, dec in radec[label_spacing::label_spacing]:
            self.text(
                label,
                ra,
                dec,
                style.label,
                collision_handler=collision_handler or self.collision_handler,
                gid="galactic-equator-label",
            )

    @use_style(PathStyle, "gridlines")
    def gridlines(
        self,
        style: PathStyle = None,
        show_labels: list = ["left", "right", "bottom"],
        lon_locations: list[float] = None,
        lat_locations: list[float] = None,
        lon_formatter_fn: Callable[[float], str] = None,
        lat_formatter_fn: Callable[[float], str] = None,
        inline: bool = True,
    ):
        """
        Plots gridlines

        Args:
            style: Styling of the gridlines. If None, then the plot's style (specified when creating the plot) will be used
            show_labels: List of locations where labels should be shown (options: "left", "right", "top", "bottom")
            az_locations: List of azimuth locations for the gridlines (in degrees, 0...360). Defaults to every 15 degrees
            alt_locations: List of altitude locations for the gridlines (in degrees, -90...90). Defaults to every 10 degrees.
            az_formatter_fn: Callable for creating labels of azimuth gridlines
            alt_formatter_fn: Callable for creating labels of altitude gridlines
            divider_line: If True, then a divider line will be plotted below the azimuth labels on the bottom of the plot (this is helpful when also plotting the horizon)
            show_ticks: If True, then tick marks will be plotted on the horizon path for every `tick_step` degree that is not also a degree label
            tick_step: Step size for tick marks
        """
        lon_formatter_fn_default = lambda lon: f"{round(lon)}\u00b0 "  # noqa: E731
        lat_formatter_fn_default = lambda lat: f"{round(lat)}\u00b0 "  # noqa: E731

        lon_formatter_fn = lon_formatter_fn or lon_formatter_fn_default
        lat_formatter_fn = lat_formatter_fn or lat_formatter_fn_default

        def lon_formatter(x, pos) -> str:
            if x < 0:
                x += 360
            return lon_formatter_fn(x)

        def lat_formatter(x, pos) -> str:
            return lat_formatter_fn(x)

        x_locations = (
            lon_locations
            if lon_locations is not None
            else [x for x in range(0, 360, 15)]
        )
        x_locations = [x - 180 for x in x_locations]
        y_locations = (
            lat_locations
            if lat_locations is not None
            else [y for y in range(-90, 90, 10)]
        )

        label_style_kwargs = style.label.matplot_kwargs(self.scale)
        label_style_kwargs.pop("va")
        label_style_kwargs.pop("ha")

        line_style_kwargs = style.line.matplot_kwargs(self.scale)
        gridlines = self.ax.gridlines(
            draw_labels=show_labels,
            x_inline=inline,
            y_inline=inline,
            rotate_labels=False,
            # xpadding=12,
            # ypadding=12,
            gid="gridlines",
            xlocs=FixedLocator(x_locations),
            xformatter=FuncFormatter(lon_formatter),
            xlabel_style=label_style_kwargs,
            ylocs=FixedLocator(y_locations),
            ylabel_style=label_style_kwargs,
            yformatter=FuncFormatter(lat_formatter),
            **line_style_kwargs,
        )
        gridlines.set_zorder(style.line.zorder)

    @cache
    def _to_ax(self, az: float, alt: float) -> tuple[float, float]:
        """Converts az/alt to axes coordinates"""
        x, y = self._proj.transform_point(az, alt, self._crs)
        data_to_axes = self.ax.transData + self.ax.transAxes.inverted()
        x_axes, y_axes = data_to_axes.transform((x, y))
        return x_axes, y_axes

    @cache
    def _ax_to_azalt(self, x: float, y: float) -> tuple[float, float]:
        trans = self.ax.transAxes + self.ax.transData.inverted()
        x_projected, y_projected = trans.transform((x, y))  # axes to data
        az, alt = self._crs.transform_point(x_projected, y_projected, self._proj)
        return float(az), float(alt)

    def _plot_background_clip_path(self):
        if self.style.has_gradient_background():
            background_color = "#ffffff00"
            self._plot_gradient_background(self.style.background_color)
        else:
            background_color = self.style.background_color.as_hex()

        self._background_clip_path = patches.Rectangle(
            (0, 0),
            width=1,
            height=1,
            facecolor=background_color,
            linewidth=0,
            fill=True,
            zorder=-3_000,
            transform=self.ax.transAxes,
        )
        self.ax.set_facecolor(background_color)

        self.ax.add_patch(self._background_clip_path)
        self._update_clip_path_polygon()

    def _init_plot(self):
        self._proj = ccrs.Mollweide(central_longitude=self.center_lon)
        self._proj.threshold = 100
        self.fig = plt.figure(
            figsize=(self.figure_size, self.figure_size),
            facecolor=self.style.figure_background_color.as_hex(),
            dpi=DPI,
        )
        self.ax = self.fig.add_subplot(1, 1, 1, projection=self._proj)
        self.fig.subplots_adjust(left=0, right=1, top=1, bottom=0)

        self.ax.xaxis.set_visible(False)
        self.ax.yaxis.set_visible(False)
        self.ax.axis("off")

        self.ax.set_global()

        self._fit_to_ax()
        self._plot_background_clip_path()
