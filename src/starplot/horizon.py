from datetime import datetime
from typing import Callable, Mapping

import pandas as pd

from cartopy import crs as ccrs
from matplotlib import pyplot as plt, patches, path
from skyfield.api import wgs84, Star as SkyfieldStar

from starplot import callables
from starplot.base import BasePlot, DPI
from starplot.data.stars import StarCatalog, STAR_NAMES
from starplot.mixins import ExtentMaskMixin
from starplot.models import Star
from starplot.plotters import StarPlotterMixin, DsoPlotterMixin
from starplot.styles import (
    PlotStyle,
    ObjectStyle,
    extensions,
    use_style,
    ZOrderEnum,
    PolygonStyle,
    PathStyle,
)

pd.options.mode.chained_assignment = None  # default='warn'

DEFAULT_OPTIC_STYLE = PlotStyle().extend(extensions.OPTIC)


class HorizonPlot(BasePlot, ExtentMaskMixin, StarPlotterMixin, DsoPlotterMixin):
    """Creates a new horizon plot.

    Args:
        optic: Optic instance that defines optical parameters
        ra: Right ascension of target center, in hours (0...24)
        dec: Declination of target center, in degrees (-90...90)
        lat: Latitude of observer's location
        lon: Longitude of observer's location
        dt: Date/time of observation (*must be timezone-aware*). Default = current UTC time.
        ephemeris: Ephemeris to use for calculating planet positions (see [Skyfield's documentation](https://rhodesmill.org/skyfield/planets.html) for details)
        style: Styling for the plot (colors, sizes, fonts, etc)
        resolution: Size (in pixels) of largest dimension of the map
        hide_colliding_labels: If True, then labels will not be plotted if they collide with another existing label
        raise_on_below_horizon: If True, then a ValueError will be raised if the target is below the horizon at the observing time/location
        scale: Scaling factor that will be applied to all relevant sizes in styles (e.g. font size, marker size, line widths, etc). For example, if you want to make everything 2x bigger, then set scale to 2.
        autoscale: If True, then the scale will be automatically set based on resolution

    Returns:
        OpticPlot: A new instance of an OpticPlot

    """

    FIELD_OF_VIEW_MAX = 9.0

    def __init__(
        self,
        lat: float,
        lon: float,
        altitude: tuple[float, float] = (0, 60),
        azimuth: tuple[float, float] = (0, 90),
        dt: datetime = None,
        ephemeris: str = "de421_2001.bsp",
        style: PlotStyle = DEFAULT_OPTIC_STYLE,
        resolution: int = 2048,
        hide_colliding_labels: bool = True,
        scale: float = 1.0,
        autoscale: bool = False,
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
            *args,
            **kwargs,
        )
        self.logger.debug("Creating HorizonPlot...")
        self.alt = altitude
        self.az = azimuth
        self.center_alt = sum(altitude) / 2
        self.center_az = sum(azimuth) / 2
        self.lat = lat
        self.lon = lon

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

    def _prepare_coords(self, ra, dec) -> (float, float):
        """Converts RA/DEC to AZ/ALT"""
        point = SkyfieldStar(ra_hours=ra, dec_degrees=dec)
        position = self.observe(point)
        pos_apparent = position.apparent()
        pos_alt, pos_az, _ = pos_apparent.altaz()
        return pos_az.degrees, pos_alt.degrees

    def _plot_kwargs(self) -> dict:
        return dict(transform=self._crs)

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

        # self.star = SkyfieldStar(ra_hours=self.ra, dec_degrees=self.dec)
        # self.position = self.observe(self.star)
        # self.pos_apparent = self.position.apparent()
        # self.pos_alt, self.pos_az, _ = self.pos_apparent.altaz()

        # if self.pos_alt.degrees < 0 and self.raise_on_below_horizon:
        #     raise ValueError("Target is below horizon at specified time/location.")

    def _adjust_radec_minmax(self):
        if self.dec_max > 70 or self.dec_min < -70:
            # naive method of getting all the stars near the poles
            self.ra_min = 0
            self.ra_max = 24

        self.dec_min -= 10
        self.dec_max += 10
        self.ra_min -= 2
        self.ra_max += 2

        # # adjust right ascension to match extent
        # if self.ra_max < 24:
        #     ra_min = (-1 * extent[1]) / 15
        #     ra_max = (-1 * extent[0]) / 15

        #     if ra_min < 0 or ra_max < 0:
        #         ra_min += 24
        #         ra_max += 24

        #     self.ra_min = ra_min
        #     self.ra_max = ra_max

        self.logger.debug(
            f"Extent = RA ({self.ra_min:.2f}, {self.ra_max:.2f}) DEC ({self.dec_min:.2f}, {self.dec_max:.2f})"
        )

    def _in_bounds_xy(self, x: float, y: float) -> bool:
        return self.in_bounds_altaz(y, x)  # alt = y, az = x

    def _prepare_star_coords(self, df):
        stars_apparent = self.observe(SkyfieldStar.from_dataframe(df)).apparent()
        nearby_stars_alt, nearby_stars_az, _ = stars_apparent.altaz()
        df["x"], df["y"] = (
            nearby_stars_az.degrees,
            nearby_stars_alt.degrees,
        )
        return df

    @use_style(PathStyle, "horizon")
    def horizon(self, style: PathStyle = None):
        # style_kwargs = style.line.matplot_kwargs(self.scale)

        bottom = patches.Polygon(
            [
                (0, 0),
                (1, 0),
                (1, -0.08),
                (0, -0.08),
                (0, 0),
            ],
            color=style.line.color.as_hex(),
            transform=self.ax.transAxes,
            clip_on=False,
        )
        self.ax.add_patch(bottom)

        self.ax.annotate(
            str(int(self.center_az)),
            (0.5, -0.04),
            xycoords=self.ax.transAxes,
            **style.label.matplot_kwargs(self.scale),
            clip_on=False,
        )

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
        self.ax.gridlines()

        # TODO : missing from optic/horizon:
        # - constellations
        # - constellation borders
        # - gridlines
        # - milky way
        
        self._plot_background_clip_path()
        self._fit_to_ax()
