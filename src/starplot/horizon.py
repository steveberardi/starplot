from datetime import datetime
from functools import cache

import pandas as pd
import geopandas as gpd

from cartopy import crs as ccrs
from matplotlib import pyplot as plt, patches
from matplotlib.ticker import FixedLocator
from skyfield.api import wgs84, Star as SkyfieldStar

from starplot.coordinates import CoordinateSystem
from starplot.base import BasePlot, DPI
from starplot.mixins import ExtentMaskMixin
from starplot.plotters import (
    ConstellationPlotterMixin,
    StarPlotterMixin,
    DsoPlotterMixin,
    MilkyWayPlotterMixin,
)
from starplot.styles import (
    PlotStyle,
    extensions,
    use_style,
    PathStyle,
)

pd.options.mode.chained_assignment = None  # default='warn'

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
    ConstellationPlotterMixin,
    StarPlotterMixin,
    DsoPlotterMixin,
    MilkyWayPlotterMixin,
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

    FIELD_OF_VIEW_MAX = 9.0

    def __init__(
        self,
        lat: float,
        lon: float,
        altitude: tuple[float, float],
        azimuth: tuple[float, float],
        dt: datetime = None,
        ephemeris: str = "de421_2001.bsp",
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
        self.center_alt = sum(altitude) / 2
        self.center_az = sum(azimuth) / 2
        self.lat = lat
        self.lon = lon

        self._geodetic = ccrs.Geodetic()
        self._plate_carree = ccrs.PlateCarree()
        self._crs = ccrs.CRS(
            proj4_params=[
                ("proj", "latlong"),
                ("a", "6378137"),
            ],
            globe=ccrs.Globe(ellipse="sphere", flattening=0),
        )

        self._calc_position()
        self._init_plot()
        self._adjust_radec_minmax()

    @cache
    def _prepare_coords(self, ra, dec) -> (float, float):
        """Converts RA/DEC to AZ/ALT"""
        point = SkyfieldStar(ra_hours=ra, dec_degrees=dec)
        position = self.observe(point).apparent()
        pos_alt, pos_az, _ = position.altaz()
        return pos_az.degrees, pos_alt.degrees

    def _prepare_star_coords(self, df):
        stars_apparent = self.observe(SkyfieldStar.from_dataframe(df)).apparent()
        nearby_stars_alt, nearby_stars_az, _ = stars_apparent.altaz()
        df["x"], df["y"] = (
            nearby_stars_az.degrees,
            nearby_stars_alt.degrees,
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
        if self.az[0] > 360 or self.az[1] > 360 and az < 90:
            az += 360

        return (
            az < self.az[1]
            and az > self.az[0]
            and alt < self.alt[1]
            and alt > self.alt[0]
        )

    def _polygon(self, points, style, **kwargs):
        super()._polygon(points, style, transform=self._crs, **kwargs)

    def _calc_position(self):
        earth = self.ephemeris["earth"]

        self.location = earth + wgs84.latlon(self.lat, self.lon)
        self.observe = self.location.at(self.timescale).observe

        locations = [
            self.location.at(self.timescale).from_altaz(
                alt_degrees=self.alt[0], az_degrees=self.az[0]
            ),  # lower left
            self.location.at(self.timescale).from_altaz(
                alt_degrees=self.alt[0], az_degrees=self.az[1]
            ),  # lower right
            self.location.at(self.timescale).from_altaz(
                alt_degrees=self.alt[1], az_degrees=self.center_az
            ),  # top center
            self.location.at(self.timescale).from_altaz(
                alt_degrees=self.center_alt, az_degrees=self.center_az
            ),  # center
            # self.location.at(self.timescale).from_altaz(alt_degrees=self.alt[1], az_degrees=self.az[0]), # upper left
            # self.location.at(self.timescale).from_altaz(alt_degrees=self.alt[1], az_degrees=self.az[1]), # upper right
        ]

        self.ra_min = None
        self.ra_max = None
        self.dec_max = None
        self.dec_min = None

        for location in locations:
            ra, dec, _ = location.radec()
            ra = ra.hours
            dec = dec.degrees
            if self.ra_min is None or ra < self.ra_min:
                self.ra_min = ra

            if self.ra_max is None or ra > self.ra_max:
                self.ra_max = ra

            if self.dec_min is None or dec < self.dec_min:
                self.dec_min = dec

            if self.dec_max is None or dec > self.dec_max:
                self.dec_max = dec

    def _adjust_radec_minmax(self):
        if self.dec_max > 70 or self.dec_min < -70:
            # naive method of getting all the stars near the poles
            self.ra_min = 0
            self.ra_max = 24

        self.dec_min -= 20
        self.dec_max += 20
        self.ra_min -= 4
        self.ra_max += 4

        if self.ra_min < 0:
            self.ra_min = 0

        self.logger.debug(
            f"Extent = RA ({self.ra_min:.2f}, {self.ra_max:.2f}) DEC ({self.dec_min:.2f}, {self.dec_max:.2f})"
        )

    def _in_bounds_xy(self, x: float, y: float) -> bool:
        return self.in_bounds_altaz(y, x)  # alt = y, az = x

    def _read_geo_package(self, filename: str):
        """Returns GeoDataFrame of a GeoPackage file"""

        # if self.ra_min <= 0 and self.ra_max >= 24:
        #     lon_min = -180
        #     lon_max = 180
        # else:
        #     lon_min = self.ra_max * 15 - 180 # ra_to_lon(24 - self.ra_max)
        #     lon_max = self.ra_min * 15 - 180 # ra_to_lon(24 - self.ra_min)

        # extent = self._extent_mask()
        # extent = (
        #     lon_min,
        #     self.dec_min,
        #     lon_max,
        #     self.dec_max,
        # )

        return gpd.read_file(
            filename,
            engine="pyogrio",
            use_arrow=True,
            # bbox=extent,
        )

    @use_style(PathStyle, "horizon")
    def horizon(
        self,
        style: PathStyle = None,
        labels: dict[int, str] = DEFAULT_HORIZON_LABELS,
        show_degree_labels: bool = True,
        degree_step: int = 15,
        show_ticks: bool = True,
        tick_step: int = 5,
    ):
        """
        Plots rectangle for horizon that shows cardinal directions and azimuth labels.

        Args:
            style: Style of the horizon path. If None, then the plot's style definition will be used.
            labels: Dictionary that maps azimuth values (0...360) to their cardinal direction labels (e.g. "N"). Default is to label each 45deg direction (e.g. "N", "NE", "E", etc)
            show_degree_labels: If True, then azimuth degree labels will be plotted on the horizon path
            degree_step: Step size for degree labels
            show_ticks: If True, then tick marks will be plotted on the horizon path for every `tick_step` degree that is not also a degree label
            tick_step: Step size for tick marks
        """
        bottom = patches.Polygon(
            [
                (0, 0),
                (1, 0),
                (1, -0.1 * self.scale),
                (0, -0.1 * self.scale),
                (0, 0),
            ],
            color=style.line.color.as_hex(),
            transform=self.ax.transAxes,
            clip_on=False,
        )
        self.ax.add_patch(bottom)

        def az_to_ax(d):
            return self._to_ax(d, self.alt[0])[0]

        for az in range(self.az[0] + 2, self.az[1], 1):
            az = int(az)

            if az >= 360:
                az -= 360

            if labels.get(az):
                self.ax.annotate(
                    labels.get(az),
                    (az_to_ax(az), -0.074 * self.scale),
                    xycoords=self.ax.transAxes,
                    **style.label.matplot_kwargs(self.scale),
                    clip_on=False,
                )

            if show_degree_labels and az % degree_step == 0:
                self.ax.annotate(
                    str(az) + "\u00b0",
                    (az_to_ax(az), -0.011 * self.scale),
                    xycoords=self.ax.transAxes,
                    **self.style.gridlines.label.matplot_kwargs(self.scale),
                    clip_on=False,
                )

            elif show_ticks and az % tick_step == 0:
                self.ax.annotate(
                    "|",
                    (az_to_ax(az), -0.011 * self.scale),
                    xycoords=self.ax.transAxes,
                    **self.style.gridlines.label.matplot_kwargs(self.scale / 2),
                    clip_on=False,
                )

        self.ax.plot(
            [0, 1],
            [-0.04 * self.scale, -0.04 * self.scale],
            lw=1,
            color=style.label.font_color.as_hex(),
            clip_on=False,
            transform=self.ax.transAxes,
        )

    @use_style(PathStyle, "gridlines")
    def gridlines(
        self,
        style: PathStyle = None,
        az_locations: list[float] = None,
        alt_locations: list[float] = None,
    ):
        """
        Plots gridlines

        Args:
            style: Styling of the gridlines. If None, then the plot's style (specified when creating the plot) will be used
            az_locations: List of azimuth locations for the gridlines (in degrees, 0...360). Defaults to every 15 degrees
            alt_locations: List of altitude locations for the gridlines (in degrees, -90...90). Defaults to every 10 degrees.

        """
        x_locations = az_locations or [x for x in range(0, 360, 15)]
        x_locations = [x - 180 for x in x_locations]
        y_locations = alt_locations or [d for d in range(-90, 90, 10)]

        line_style_kwargs = style.line.matplot_kwargs()
        gridlines = self.ax.gridlines(
            draw_labels=False,
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
        gridlines.xlocator = FixedLocator(x_locations)
        gridlines.ylocator = FixedLocator(y_locations)

    @cache
    def _to_ax(self, az: float, alt: float) -> tuple[float, float]:
        """Converts az/alt to axes coordinates"""
        x, y = self._proj.transform_point(az, alt, self._crs)
        data_to_axes = self.ax.transData + self.ax.transAxes.inverted()
        x_axes, y_axes = data_to_axes.transform((x, y))
        return x_axes, y_axes

    def _fit_to_ax(self) -> None:
        bbox = self.ax.get_window_extent().transformed(
            self.fig.dpi_scale_trans.inverted()
        )
        width, height = bbox.width, bbox.height
        self.fig.set_size_inches(width, height)

    def _plot_background_clip_path(self):
        self._background_clip_path = patches.Rectangle(
            (0, 0),
            width=1,
            height=1,
            facecolor=self.style.background_color.as_hex(),
            linewidth=0,
            fill=True,
            zorder=-3_000,
            transform=self.ax.transAxes,
        )

        self.ax.add_patch(self._background_clip_path)

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

        self._plot_background_clip_path()
        self._fit_to_ax()
