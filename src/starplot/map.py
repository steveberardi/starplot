import datetime
import math
from typing import Callable
from functools import cache

from cartopy import crs as ccrs
from matplotlib import pyplot as plt
from matplotlib import path, patches, ticker
from matplotlib.ticker import FuncFormatter, FixedLocator
from shapely import Polygon
from skyfield.api import wgs84
import numpy as np

from starplot.coordinates import CoordinateSystem
from starplot import geod
from starplot.base import BasePlot, DPI
from starplot.mixins import ExtentMaskMixin
from starplot.plotters import (
    ConstellationPlotterMixin,
    StarPlotterMixin,
    DsoPlotterMixin,
    MilkyWayPlotterMixin,
)
from starplot.projections import Projection
from starplot.styles import (
    ObjectStyle,
    LabelStyle,
    PlotStyle,
    PathStyle,
)
from starplot.styles.helpers import use_style
from starplot.utils import lon_to_ra, ra_to_lon


DEFAULT_MAP_STYLE = PlotStyle()  # .extend(extensions.MAP)


class MapPlot(
    BasePlot,
    ExtentMaskMixin,
    StarPlotterMixin,
    DsoPlotterMixin,
    MilkyWayPlotterMixin,
    ConstellationPlotterMixin,
):
    """Creates a new map plot.

    !!! star "Note"
        **`lat`, `lon`, and `dt` are required for perspective projections (`Orthographic`, `Stereographic`, and `Zenith`)**

    Args:
        projection: Projection of the map
        ra_min: Minimum right ascension of the map's extent, in degrees (0...360)
        ra_max: Maximum right ascension of the map's extent, in degrees (0...360)
        dec_min: Minimum declination of the map's extent, in degrees (-90...90)
        dec_max: Maximum declination of the map's extent, in degrees (-90...90)
        lat: Latitude for perspective projections: Orthographic, Stereographic, and Zenith
        lon: Longitude for perspective projections: Orthographic, Stereographic, and Zenith
        dt: Date/time to use for star/planet positions, (*must be timezone-aware*). Default = current UTC time.
        ephemeris: Ephemeris to use for calculating planet positions (see [Skyfield's documentation](https://rhodesmill.org/skyfield/planets.html) for details)
        style: Styling for the plot (colors, sizes, fonts, etc)
        resolution: Size (in pixels) of largest dimension of the map
        hide_colliding_labels: If True, then labels will not be plotted if they collide with another existing label
        clip_path: An optional Shapely Polygon that specifies the clip path of the plot -- only objects inside the polygon will be plotted. If `None` (the default), then the clip path will be the extent of the map you specified with the RA/DEC parameters.
        scale: Scaling factor that will be applied to all sizes in styles (e.g. font size, marker size, line widths, etc). For example, if you want to make everything 2x bigger, then set the scale to 2. At `scale=1` and `resolution=4096` (the default), all sizes are optimized visually for a map that covers 1-3 constellations. So, if you're creating a plot of a _larger_ extent, then it'd probably be good to decrease the scale (i.e. make everything smaller) -- and _increase_ the scale if you're plotting a very small area.
        autoscale: If True, then the scale will be set automatically based on resolution.
        suppress_warnings: If True (the default), then all warnings will be suppressed

    Returns:
        MapPlot: A new instance of a MapPlot

    """

    _coordinate_system = CoordinateSystem.RA_DEC

    def __init__(
        self,
        projection: Projection,
        ra_min: float = 0,
        ra_max: float = 360,
        dec_min: float = -90,
        dec_max: float = 90,
        lat: float = None,
        lon: float = None,
        dt: datetime = None,
        ephemeris: str = "de421_2001.bsp",
        style: PlotStyle = DEFAULT_MAP_STYLE,
        resolution: int = 4096,
        hide_colliding_labels: bool = True,
        clip_path: Polygon = None,
        scale: float = 1.0,
        autoscale: bool = False,
        suppress_warnings: bool = True,
        *args,
        **kwargs,
    ) -> "MapPlot":
        super().__init__(
            dt,
            ephemeris,
            style,
            resolution,
            hide_colliding_labels,
            scale=scale,
            autoscale=autoscale,
            suppress_warnings=suppress_warnings,
            *args,
            **kwargs,
        )
        self.logger.debug("Creating MapPlot...")

        if ra_min > ra_max:
            raise ValueError("ra_min must be less than ra_max")
        if dec_min > dec_max:
            raise ValueError("dec_min must be less than dec_max")
        if dec_min < -90 or dec_max > 90:
            raise ValueError("Declination out of range (must be -90...90)")

        self.projection = projection
        self.ra_min = ra_min
        self.ra_max = ra_max
        self.dec_min = dec_min
        self.dec_max = dec_max
        self.lat = lat
        self.lon = lon
        self.clip_path = clip_path

        if self.projection in [
            Projection.ORTHOGRAPHIC,
            Projection.STEREOGRAPHIC,
            Projection.ZENITH,
        ] and (lat is None or lon is None):
            raise ValueError(
                f"lat and lon are required for the {self.projection.value.upper()} projection"
            )

        if self.projection == Projection.ZENITH and not self._is_global_extent():
            raise ValueError(
                "Zenith projection requires a global extent: ra_min=0, ra_max=360, dec_min=-90, dec_max=90"
            )

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

    def _plot_kwargs(self) -> dict:
        return dict(transform=self._crs)

    @cache
    def in_bounds(self, ra: float, dec: float) -> bool:
        """Determine if a coordinate is within the bounds of the plot.

        Args:
            ra: Right ascension, in degrees (0...360)
            dec: Declination, in degrees (-90...90)

        Returns:
            True if the coordinate is in bounds, otherwise False
        """
        # TODO : try using pyproj transformer directly
        x, y = self._proj.transform_point(ra, dec, self._crs)
        data_to_axes = self.ax.transData + self.ax.transAxes.inverted()
        x_axes, y_axes = data_to_axes.transform((x, y))
        return 0 <= x_axes <= 1 and 0 <= y_axes <= 1

    def _in_bounds_xy(self, x: float, y: float) -> bool:
        return self.in_bounds(x, y)

    def _polygon(self, points, style, **kwargs):
        super()._polygon(points, style, transform=self._crs, **kwargs)

    def _latlon_bounds(self):
        # convert the RA/DEC bounds to lat/lon bounds
        return [
            -1 * self.ra_min,
            -1 * self.ra_max,
            self.dec_min,
            self.dec_max,
        ]

    def _adjust_radec_minmax(self):
        # adjust declination to match extent
        extent = self.ax.get_extent(crs=self._plate_carree)
        self.dec_min = extent[2]
        self.dec_max = extent[3]

        # adjust the RA min/max if the DEC bounds is near the poles
        if self.projection in [Projection.STEREO_NORTH, Projection.STEREO_SOUTH] and (
            self.dec_max > 80 or self.dec_min < -80
        ):
            self.ra_min = 0
            self.ra_max = 360

        elif self.ra_max < 360:
            # adjust right ascension to match extent
            ra_min = extent[1] * -1
            ra_max = extent[0] * -1

            if ra_min < 0 or ra_max < 0:
                ra_min += 360
                ra_max += 360

            self.ra_min = ra_min
            self.ra_max = ra_max

        else:
            self.ra_min = lon_to_ra(extent[1]) * 15
            self.ra_max = lon_to_ra(extent[0]) * 15 + 360

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
        if self.lat is None or self.lon is None or self.dt is None:
            raise ValueError("lat, lon, and dt are required for plotting the zenith")

        geographic = wgs84.latlon(latitude_degrees=self.lat, longitude_degrees=self.lon)
        observer = geographic.at(self.timescale)
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
        if self.lat is None or self.lon is None or self.dt is None:
            raise ValueError("lat, lon, and dt are required for plotting the horizon")

        geographic = wgs84.latlon(latitude_degrees=self.lat, longitude_degrees=self.lon)
        observer = geographic.at(self.timescale)
        zenith = observer.from_altaz(alt_degrees=90, az_degrees=0)
        ra, dec, _ = zenith.radec()

        points = geod.ellipse(
            center=(ra.hours * 15, dec.degrees),
            height_degrees=180,
            width_degrees=180,
            num_pts=100,
        )
        x = []
        y = []

        for ra, dec in points:
            x0, y0 = self._prepare_coords(ra, dec)
            x.append(x0)
            y.append(y0)

        style_kwargs = {}
        if self.projection == Projection.ZENITH:
            """
            For zenith projections, we plot the horizon as a patch to make a more perfect circle
            """
            style_kwargs = style.line.matplot_kwargs(self.scale)
            style_kwargs["clip_on"] = False
            style_kwargs["edgecolor"] = style_kwargs.pop("color")
            patch = patches.Circle(
                (0.50, 0.50),
                radius=0.454,
                facecolor=None,
                fill=False,
                transform=self.ax.transAxes,
                **style_kwargs,
            )
            self.ax.add_patch(patch)
            self._background_clip_path = patch
            self._update_clip_path_polygon(
                buffer=style.line.width / 2 + 2 * style.line.edge_width + 20
            )

            if not labels:
                return

            label_ax_coords = [
                (0.5, 0.95),  # north
                (0.045, 0.5),  # east
                (0.5, 0.045),  # south
                (0.954, 0.5),  # west
            ]
            for label, coords in zip(labels, label_ax_coords):
                self.ax.annotate(
                    label,
                    coords,
                    xycoords=self.ax.transAxes,
                    clip_on=False,
                    **style.label.matplot_kwargs(self.scale),
                )

            return

        else:
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

        def ra_formatter(x, pos) -> str:
            ra = lon_to_ra(x)
            return ra_formatter_fn(ra)

        def dec_formatter(x, pos) -> str:
            return dec_formatter_fn(x)

        ra_locations = ra_locations or [x for x in range(0, 360, 15)]
        dec_locations = dec_locations or [d for d in range(-80, 90, 10)]

        line_style_kwargs = style.line.matplot_kwargs()
        gridlines = self.ax.gridlines(
            draw_labels=labels,
            x_inline=False,
            y_inline=False,
            rotate_labels=False,
            xpadding=12,
            ypadding=12,
            clip_on=True,
            clip_path=self._background_clip_path,
            gid="gridlines",
            **line_style_kwargs,
        )

        if labels:
            self._axis_labels = True

        label_style_kwargs = style.label.matplot_kwargs()
        label_style_kwargs.pop("va")
        label_style_kwargs.pop("ha")

        if self.dec_max > 75 or self.dec_min < -75:
            # if the extent is near the poles, then plot the RA gridlines again
            # because cartopy does not extend lines to poles
            for ra in ra_locations:
                self.ax.plot(
                    (ra, ra),
                    (-90, 90),
                    gid="gridlines",
                    **line_style_kwargs,
                    **self._plot_kwargs(),
                )

        gridlines.xlocator = FixedLocator([ra_to_lon(r / 15) for r in ra_locations])
        gridlines.xformatter = FuncFormatter(ra_formatter)
        gridlines.xlabel_style = label_style_kwargs

        gridlines.ylocator = FixedLocator(dec_locations)
        gridlines.yformatter = FuncFormatter(dec_formatter)
        gridlines.ylabel_style = label_style_kwargs

        if tick_marks:
            self._tick_marks(style, ra_tick_locations, dec_tick_locations)

    def _tick_marks(self, style, ra_tick_locations=None, dec_tick_locations=None):
        def in_axes(ra):
            return self.in_bounds(ra, (self.dec_max + self.dec_min) / 2)

        xticks = ra_tick_locations or [x for x in np.arange(0, 360, 1.875)]
        yticks = dec_tick_locations or [x for x in np.arange(-90, 90, 1)]

        inbound_xticks = [ra_to_lon(ra / 15) for ra in xticks if in_axes(ra)]
        self.ax.set_xticks(inbound_xticks, crs=self._plate_carree)
        self.ax.xaxis.set_major_formatter(ticker.NullFormatter())

        inbound_yticks = [y for y in yticks if y < self.dec_max and y > self.dec_min]
        self.ax.set_yticks(inbound_yticks, crs=self._plate_carree)
        self.ax.yaxis.set_major_formatter(ticker.NullFormatter())

        self.ax.tick_params(
            which="major",
            width=1,
            length=8,
            color=style.label.font_color.as_hex(),
            top=True,
            right=True,
        )

    def _fit_to_ax(self) -> None:
        bbox = self.ax.get_window_extent().transformed(
            self.fig.dpi_scale_trans.inverted()
        )
        width, height = bbox.width, bbox.height
        self.fig.set_size_inches(width, height)

    def _init_plot(self):
        self.fig = plt.figure(
            figsize=(self.figure_size, self.figure_size),
            facecolor=self.style.figure_background_color.as_hex(),
            layout="constrained",
            dpi=DPI,
        )
        bounds = self._latlon_bounds()
        center_lat = (bounds[2] + bounds[3]) / 2
        center_lon = (bounds[0] + bounds[1]) / 2
        self._center_lat = center_lat
        self._center_lon = center_lon

        if self.projection in [
            Projection.ORTHOGRAPHIC,
            Projection.STEREOGRAPHIC,
            Projection.ZENITH,
        ]:
            # Calculate local sidereal time (LST) to shift RA DEC to be in line with current date and time
            lst = -(360.0 * self.timescale.gmst / 24.0 + self.lon) % 360.0
            self._proj = Projection.crs(self.projection, lon=lst, lat=self.lat)
        elif self.projection == Projection.LAMBERT_AZ_EQ_AREA:
            self._proj = Projection.crs(
                self.projection, center_lat=center_lat, center_lon=center_lon
            )
        else:
            self._proj = Projection.crs(self.projection, center_lon)
        self._proj.threshold = 1000
        self.ax = plt.axes(projection=self._proj)

        if self._is_global_extent():
            if self.projection == Projection.ZENITH:
                theta = np.linspace(0, 2 * np.pi, 100)
                center, radius = [0.5, 0.5], 0.45
                verts = np.vstack([np.sin(theta), np.cos(theta)]).T
                circle = path.Path(verts * radius + center)
                extent = self.ax.get_extent(crs=self._proj)
                self.ax.set_extent((p / 3.548 for p in extent), crs=self._proj)
                self.ax.set_boundary(circle, transform=self.ax.transAxes)
            else:
                # this cartopy function works better for setting global extents
                self.ax.set_global()
        else:
            self.ax.set_extent(bounds, crs=self._plate_carree)

        self.ax.set_facecolor(self.style.background_color.as_hex())
        self._adjust_radec_minmax()

        self.logger.debug(f"Projection = {self.projection.value.upper()}")

        self._fit_to_ax()
        self._plot_background_clip_path()

    @use_style(LabelStyle, "info_text")
    def info(self, style: LabelStyle = None):
        """
        Plots info text in the lower left corner, including date/time and lat/lon.

        _Only available for ZENITH projections_

        Args:
            style: Styling of the info text. If None, then the plot's style definition will be used.
        """
        if not self.projection == Projection.ZENITH:
            raise NotImplementedError("info text only available for zenith projections")

        dt_str = self.dt.strftime("%m/%d/%Y @ %H:%M:%S") + " " + self.dt.tzname()
        info = f"{str(self.lat)}, {str(self.lon)}\n{dt_str}"
        self.ax.text(
            0.05,
            0.05,
            info,
            transform=self.ax.transAxes,
            **style.matplot_kwargs(self.scale),
        )

    def _ax_to_radec(self, x, y):
        trans = self.ax.transAxes + self.ax.transData.inverted()
        x_projected, y_projected = trans.transform((x, y))  # axes to data
        x_ra, y_ra = self._crs.transform_point(x_projected, y_projected, self._proj)
        return (x_ra + 360), y_ra

    def _plot_background_clip_path(self):
        def to_axes(points):
            ax_points = []

            for ra, dec in points:
                x, y = self._proj.transform_point(ra, dec, self._crs)
                data_to_axes = self.ax.transData + self.ax.transAxes.inverted()
                x_axes, y_axes = data_to_axes.transform((x, y))
                ax_points.append([x_axes, y_axes])
            return ax_points

        if self.clip_path is not None:
            points = list(zip(*self.clip_path.exterior.coords.xy))
            self._background_clip_path = patches.Polygon(
                to_axes(points),
                facecolor=self.style.background_color.as_hex(),
                fill=True,
                zorder=-2_000,
                transform=self.ax.transAxes,
            )
        elif self.projection == Projection.ZENITH:
            self._background_clip_path = patches.Circle(
                (0.50, 0.50),
                radius=0.45,
                fill=True,
                facecolor=self.style.background_color.as_hex(),
                # edgecolor=self.style.border_line_color.as_hex(),
                linewidth=0,
                zorder=-2_000,
                transform=self.ax.transAxes,
            )
        else:
            # draw patch in axes coords, which are easier to work with
            # in cases like this cause they go from 0...1 in all plots
            self._background_clip_path = patches.Rectangle(
                (0, 0),
                width=1,
                height=1,
                facecolor=self.style.background_color.as_hex(),
                linewidth=0,
                fill=True,
                zorder=-2_000,
                transform=self.ax.transAxes,
            )

        self.ax.add_patch(self._background_clip_path)
        self._update_clip_path_polygon()
