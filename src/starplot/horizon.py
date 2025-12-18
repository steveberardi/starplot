import math

from functools import cache
from typing import Callable

from cartopy import crs as ccrs
from matplotlib import pyplot as plt, patches
from matplotlib.ticker import FixedLocator, FuncFormatter
from skyfield.api import wgs84, Star as SkyfieldStar
from shapely import Point, Polygon, MultiPolygon
from starplot.coordinates import CoordinateSystem
from starplot.base import BasePlot, DPI
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
from starplot.styles import (
    PlotStyle,
    extensions,
    use_style,
    PathStyle,
    GradientDirection,
)

DEFAULT_HORIZON_STYLE = PlotStyle().extend(extensions.MAP)

DEFAULT_HORIZON_LABELS = {
    0: "N",
    45: "NE",
    90: "E",
    135: "SE",
    180: "S",
    225: "SW",
    270: "W",
    315: "NW",
}


class HorizonPlot(
    BasePlot,
    ExtentMaskMixin,
    # HorizonExtentMaskMixin,
    ConstellationPlotterMixin,
    StarPlotterMixin,
    DsoPlotterMixin,
    MilkyWayPlotterMixin,
    GradientBackgroundMixin,
    LegendPlotterMixin,
    ArrowPlotterMixin,
):
    """Creates a new horizon plot.

    Args:
        lat: Latitude of observer's location
        lon: Longitude of observer's location
        altitude: Tuple of altitude range to plot (min, max)
        azimuth: Tuple of azimuth range to plot (min, max)
        dt: Date/time of observation (*must be timezone-aware*). Default = current UTC time.
        ephemeris: Ephemeris to use for calculating planet positions (see [Skyfield's documentation](https://rhodesmill.org/skyfield/planets.html) for details)
        style: Styling for the plot (colors, sizes, fonts, etc)
        resolution: Size (in pixels) of largest dimension of the map
        hide_colliding_labels: If True, then labels will not be plotted if they collide with another existing label
        scale: Scaling factor that will be applied to all relevant sizes in styles (e.g. font size, marker size, line widths, etc). For example, if you want to make everything 2x bigger, then set scale to 2.
        autoscale: If True, then the scale will be automatically set based on resolution
        suppress_warnings: If True (the default), then all warnings will be suppressed

    Returns:
        HorizonPlot: A new instance of an HorizonPlot

    """

    _coordinate_system = CoordinateSystem.AZ_ALT
    _gradient_direction = GradientDirection.LINEAR

    FIELD_OF_VIEW_MAX = 9.0

    def __init__(
        self,
        altitude: tuple[float, float],
        azimuth: tuple[float, float],
        observer: Observer = Observer(),
        ephemeris: str = "de421.bsp",
        style: PlotStyle = DEFAULT_HORIZON_STYLE,
        resolution: int = 4096,
        hide_colliding_labels: bool = True,
        scale: float = 1.0,
        autoscale: bool = False,
        suppress_warnings: bool = True,
        *args,
        **kwargs,
    ) -> "HorizonPlot":
        super().__init__(
            observer,
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

        if azimuth[0] >= azimuth[1]:
            raise ValueError("Azimuth min must be less than max")
        if azimuth[1] - azimuth[0] > 180:
            raise ValueError("Azimuth range cannot be greater than 180 degrees")

        if altitude[0] >= altitude[1]:
            raise ValueError("Altitude min must be less than max")
        if altitude[1] - altitude[0] > 90:
            raise ValueError("Altitude range cannot be greater than 90 degrees")

        self.logger.debug("Creating HorizonPlot...")
        self.alt = altitude
        self.az = azimuth
        self._alt = altitude
        self._az = azimuth
        self.center_alt = sum(altitude) / 2
        self.center_az = sum(azimuth) / 2

        self._geodetic = ccrs.Geodetic()
        self._plate_carree = ccrs.PlateCarree()
        self._crs = ccrs.CRS(
            proj4_params=[
                ("proj", "latlong"),
                ("a", "6378137"),
            ],
            globe=ccrs.Globe(ellipse="sphere", flattening=0),
        )

        self._init_plot()

        self.altaz_mask = self._extent_mask_altaz()
        self.logger.debug(f"Extent = AZ ({self.az}) ALT ({self.alt})")

        self._calc_position()

    @cache
    def _prepare_coords(self, ra, dec) -> (float, float):
        """Converts RA/DEC to AZ/ALT"""
        if ra > 360:
            ra -= 360
        if ra < 0:
            ra += 360
        point = SkyfieldStar(ra_hours=ra / 15, dec_degrees=dec)
        position = self.observe(point).apparent()
        pos_alt, pos_az, _ = position.altaz()
        return pos_az.degrees, pos_alt.degrees

    def _prepare_star_coords(self, df, limit_by_altaz=True):
        # import geopandas as gpd

        # Skyfield needs these columns
        df["ra_hours"], df["dec_degrees"] = (df.ra / 15, df.dec)

        stars_apparent = self.observe(SkyfieldStar.from_dataframe(df)).apparent()
        nearby_stars_alt, nearby_stars_az, _ = stars_apparent.altaz()
        df["x"], df["y"] = (
            nearby_stars_az.degrees,
            nearby_stars_alt.degrees,
        )
        # if limit_by_altaz:
        #     extent = self._extent_mask_altaz()
        #     df["_geometry_az_alt"] = gpd.points_from_xy(df.x, df.y)
        #     df = df[df["_geometry_az_alt"].intersects(extent)]

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
        az, alt = self._prepare_coords(ra, dec)
        return self.in_bounds_altaz(alt, az)

    def in_bounds_altaz(self, alt, az, scale: float = 1) -> bool:
        """Determine if a coordinate is within the bounds of the plot.

        Args:
            alt: Altitude angle in degrees (0...90)
            az: Azimuth angle in degrees (0...360)

        Returns:
            True if the coordinate is in bounds, otherwise False
        """
        return self.altaz_mask.contains(Point(az, alt))

    def _in_bounds_xy(self, x: float, y: float) -> bool:
        return self.in_bounds_altaz(y, x)  # alt = y, az = x

    def _polygon(self, points, style, **kwargs):
        super()._polygon(points, style, transform=self._crs, **kwargs)

    def _calc_position(self):
        earth = self.ephemeris["earth"]
        self.location = earth + wgs84.latlon(self.observer.lat, self.observer.lon)
        self.observe = self.location.at(self.observer.timescale).observe

        # locations = [
        #     self.location.at(self.timescale).from_altaz(
        #         alt_degrees=self.alt[0], az_degrees=self.az[0]
        #     ),  # lower left
        #     self.location.at(self.timescale).from_altaz(
        #         alt_degrees=self.alt[0], az_degrees=self.az[1]
        #     ),  # lower right
        #     self.location.at(self.timescale).from_altaz(
        #         alt_degrees=self.alt[1], az_degrees=self.center_az
        #     ),  # top center
        #     self.location.at(self.timescale).from_altaz(
        #         alt_degrees=self.center_alt, az_degrees=self.center_az
        #     ),  # center
        #     self.location.at(self.timescale).from_altaz(alt_degrees=self.alt[1], az_degrees=self.az[0]), # upper left
        #     self.location.at(self.timescale).from_altaz(alt_degrees=self.alt[1], az_degrees=self.az[1]), # upper right
        # ]

        # self.ra_min = None
        # self.ra_max = None
        # self.dec_max = None
        # self.dec_min = None
        # print(self.alt)
        # print(self.az)
        # for location in locations:
        #     ra, dec, _ = location.radec()
        #     ra = ra.hours
        #     dec = dec.degrees
        #     print(ra, dec)
        #     if self.ra_min is None or ra < self.ra_min:
        #         self.ra_min = ra

        #     if self.ra_max is None or ra > self.ra_max:
        #         self.ra_max = ra

        #     if self.dec_min is None or dec < self.dec_min:
        #         self.dec_min = dec

        #     if self.dec_max is None or dec > self.dec_max:
        #         self.dec_max = dec

        # if self.dec_max > 70 or self.dec_min < -70:
        #     # naive method of getting all the stars near the poles
        #     self.ra_min = 0
        #     self.ra_max = 24
        # else:
        #     self.ra_min = max(self.ra_min - 4, 0)
        #     self.ra_max = min(self.ra_max + 4, 24)

        # self.dec_min -= 10
        # self.dec_max += 10

        self.ra_min = 0
        self.ra_max = 360
        self.dec_min = self.observer.lat - 90
        self.dec_max = self.observer.lat + 90

        self.logger.debug(
            f"Extent = RA ({self.ra_min:.2f}, {self.ra_max:.2f}) DEC ({self.dec_min:.2f}, {self.dec_max:.2f})"
        )

    @cache
    def _extent_mask_altaz(self):
        """
        Returns shapely geometry objects of the alt/az extent

        If the extent crosses North cardinal direction, then a MultiPolygon will be returned
        """
        extent = list(self.ax.get_extent(crs=self._plate_carree))
        alt_min, alt_max = extent[2], extent[3]
        az_min, az_max = extent[0], extent[1]

        az_ul, _ = self._ax_to_azalt(0, 1)
        az_ur, _ = self._ax_to_azalt(1, 1)

        if az_ul < 0:
            az_ul += 360

        if az_ur < 0:
            az_ur += 360

        az_min = min(self.az[0], self.az[1], az_ul, az_ur)
        az_max = max(self.az[0], self.az[1], az_ul, az_ur)

        if az_min < 0:
            az_min += 360
        if az_max < 0:
            az_max += 360

        if az_min >= az_max:
            az_max += 360

        self.az = (az_min, az_max)
        self.alt = (alt_min, alt_max)

        if az_max <= 360:
            coords = [
                [az_min, alt_min],
                [az_max, alt_min],
                [az_max, alt_max],
                [az_min, alt_max],
                [az_min, alt_min],
            ]
            return Polygon(coords)

        else:
            coords_1 = [
                [az_min, alt_min],
                [360, alt_min],
                [360, alt_max],
                [az_min, alt_max],
                [az_min, alt_min],
            ]
            coords_2 = [
                [0, alt_min],
                [az_max - 360, alt_min],
                [az_max - 360, alt_max],
                [0, alt_max],
                [0, alt_min],
            ]

            return MultiPolygon(
                [
                    Polygon(coords_1),
                    Polygon(coords_2),
                ]
            )

    @use_style(PathStyle, "horizon")
    def horizon(
        self,
        style: PathStyle = None,
        labels: dict[int, str] = DEFAULT_HORIZON_LABELS,
    ):
        """
        Plots rectangle for horizon that shows cardinal directions and azimuth labels.

        Args:
            style: Style of the horizon path. If None, then the plot's style definition will be used.
            labels: Dictionary that maps azimuth values (0...360) to their cardinal direction labels (e.g. "N"). Default is to label each 45deg direction (e.g. "N", "NE", "E", etc)
        """
        patch_y = -0.11 * self.scale
        bottom = patches.Polygon(
            [
                (0, -0.04 * self.scale),
                (1, -0.04 * self.scale),
                (1, patch_y),
                (0, patch_y),
                (0, -0.04 * self.scale),
            ],
            color=style.line.color.as_hex(),
            transform=self.ax.transAxes,
            clip_on=False,
        )
        self.ax.add_patch(bottom)

        for az, label in labels.items():
            az = int(az)
            x, _ = self._to_ax(az, self.alt[0])
            if x <= 0.03 or x >= 0.97 or math.isnan(x):
                continue

            self.ax.annotate(
                label,
                (x, patch_y + 0.027),
                xycoords=self.ax.transAxes,
                xytext=(
                    style.label.offset_x * self.scale,
                    style.label.offset_y * self.scale,
                ),
                textcoords="offset points",
                **style.label.matplot_kwargs(self.scale),
                clip_on=False,
            )

    @use_style(PathStyle, "gridlines")
    def gridlines(
        self,
        style: PathStyle = None,
        show_labels: list = ["left", "right", "bottom"],
        az_locations: list[float] = None,
        alt_locations: list[float] = None,
        az_formatter_fn: Callable[[float], str] = None,
        alt_formatter_fn: Callable[[float], str] = None,
        divider_line: bool = True,
        show_ticks: bool = True,
        tick_step: int = 5,
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
        az_formatter_fn_default = lambda az: f"{round(az)}\u00b0 "  # noqa: E731
        alt_formatter_fn_default = lambda alt: f"{round(alt)}\u00b0 "  # noqa: E731

        az_formatter_fn = az_formatter_fn or az_formatter_fn_default
        alt_formatter_fn = alt_formatter_fn or alt_formatter_fn_default

        def az_formatter(x, pos) -> str:
            if x < 0:
                x += 360
            return az_formatter_fn(x)

        def alt_formatter(x, pos) -> str:
            return alt_formatter_fn(x)

        x_locations = az_locations or [x for x in range(0, 360, 15)]
        x_locations = [x - 180 for x in x_locations]
        y_locations = alt_locations or [d for d in range(-90, 90, 10)]

        label_style_kwargs = style.label.matplot_kwargs()
        label_style_kwargs.pop("va")
        label_style_kwargs.pop("ha")

        line_style_kwargs = style.line.matplot_kwargs()
        gridlines = self.ax.gridlines(
            draw_labels=show_labels,
            x_inline=False,
            y_inline=False,
            rotate_labels=False,
            xpadding=12,
            ypadding=12,
            gid="gridlines",
            xlocs=FixedLocator(x_locations),
            xformatter=FuncFormatter(az_formatter),
            xlabel_style=label_style_kwargs,
            ylocs=FixedLocator(y_locations),
            ylabel_style=label_style_kwargs,
            yformatter=FuncFormatter(alt_formatter),
            **line_style_kwargs,
        )
        gridlines.set_zorder(style.line.zorder)

        if show_labels:
            self._axis_labels = True

        # gridlines.xlocator = FixedLocator(x_locations)
        # gridlines.xformatter = FuncFormatter(az_formatter)
        # gridlines.xlabel_style = label_style_kwargs

        # gridlines.ylocator = FixedLocator(y_locations)
        # gridlines.yformatter = FuncFormatter(alt_formatter)
        # gridlines.ylabel_style = label_style_kwargs
        # print(gridlines.label_artists)
        # for label in gridlines.label_artists:
        #     label.set_zorder(style.label.zorder)

        if divider_line:
            self.ax.plot(
                [0, 1],
                [-0.04 * self.scale, -0.04 * self.scale],
                lw=1,
                color=style.label.font_color.as_hex(),
                clip_on=False,
                transform=self.ax.transAxes,
            )

        if not show_ticks or len(x_locations) < 2:
            return

        # sort x locations so we iterate in order
        x_locations_sorted = sorted(x_locations)
        for i, az in enumerate(x_locations_sorted[1:], start=1):
            prev_az = x_locations_sorted[i - 1]

            # start at az label location + tick step cause we only want ticks between labels
            for az_tick in range(prev_az + tick_step, az, tick_step):
                a = int(az_tick)
                if a >= 360:
                    a -= 360
                x, _ = self._to_ax(a, self.alt[0])

                if x <= 0.03 or x >= 0.97 or math.isnan(x):
                    continue

                self.ax.annotate(
                    "|",
                    (x, -0.011 * self.scale),
                    xycoords=self.ax.transAxes,
                    **style.label.matplot_kwargs(self.scale / 2),
                )

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

    def _fit_to_ax(self) -> None:
        bbox = self.ax.get_window_extent().transformed(
            self.fig.dpi_scale_trans.inverted()
        )
        width, height = bbox.width, bbox.height
        self.fig.set_size_inches(width, height)

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
        self._proj = ccrs.LambertAzimuthalEqualArea(
            central_longitude=sum(self.az) / 2,
            central_latitude=0,
        )
        self._proj.threshold = 100
        self.fig = plt.figure(
            figsize=(self.figure_size, self.figure_size),
            facecolor=self.style.figure_background_color.as_hex(),
            layout="constrained",
            dpi=DPI,
        )
        self.ax = plt.axes(projection=self._proj)
        self.ax.xaxis.set_visible(False)
        self.ax.yaxis.set_visible(False)
        self.ax.axis("off")

        bounds = [
            self.az[0],
            self.az[1],
            self.alt[0],
            self.alt[1],
        ]

        self.ax.set_extent(bounds, crs=ccrs.PlateCarree())

        self._fit_to_ax()

        # if self.gradient_preset:
        #     self.apply_gradient_background(self.gradient_preset)

        self._plot_background_clip_path()
