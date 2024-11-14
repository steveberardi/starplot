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
from starplot.optics import Optic
from starplot.plotters import StarPlotterMixin, DsoPlotterMixin
from starplot.styles import (
    PlotStyle,
    ObjectStyle,
    LabelStyle,
    extensions,
    use_style,
    ZOrderEnum,
)
from starplot.utils import azimuth_to_string

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
    ) -> "OpticPlot":
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
        return (
            az < self.az[1]
            and az > self.az[0]
            and alt < self.alt[1]
            and alt > self.alt[0]
        )

    def in_bounds_altaz(self, alt, az, scale: float = 1) -> bool:
        """Determine if a coordinate is within the bounds of the plot.

        Args:
            alt: Altitude angle in degrees (0...90)
            az: Azimuth angle in degrees (0...360)

        Returns:
            True if the coordinate is in bounds, otherwise False
        """
        # x, y = self._proj.transform_point(az, alt, self._crs)
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

        # get radec at center horizon
        center = self.location.at(self.timescale).from_altaz(
            alt_degrees=0, az_degrees=self.center_az
        )
        print(self.center_az)
        print(center.radec())
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
        # self.ra_min = self.ra - self.optic.true_fov / 15 * 1.08
        # self.ra_max = self.ra + self.optic.true_fov / 15 * 1.08
        # self.dec_max = self.dec + self.optic.true_fov / 2 * 1.03
        # self.dec_min = self.dec - self.optic.true_fov / 2 * 1.03

        if self.dec_max > 70 or self.dec_min < -70:
            # naive method of getting all the stars near the poles
            self.ra_min = 0
            self.ra_max = 24

        # TODO : below are in ra/dec - need to convert to alt/az
        # adjust declination to match extent
        extent = self.ax.get_extent(crs=ccrs.PlateCarree())
        self.dec_min = extent[2]
        self.dec_max = extent[3]

        # adjust right ascension to match extent
        if self.ra_max < 24:
            ra_min = (-1 * extent[1]) / 15
            ra_max = (-1 * extent[0]) / 15

            if ra_min < 0 or ra_max < 0:
                ra_min += 24
                ra_max += 24

            self.ra_min = ra_min
            self.ra_max = ra_max

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

    def _scatter_stars(self, ras, decs, sizes, alphas, colors, style=None, **kwargs):
        plotted = super()._scatter_stars(
            ras, decs, sizes, alphas, colors, style, **kwargs
        )

        if type(self._background_clip_path) == patches.Rectangle:
            # convert to generic path to handle possible rotation angle:
            clip_path = path.Path(self._background_clip_path.get_corners())
            plotted.set_clip_path(clip_path, transform=self.ax.transData)
        else:
            plotted.set_clip_path(self._background_clip_path)

    @use_style(ObjectStyle, "star")
    def stars(
        self,
        mag: float = 6.0,
        catalog: StarCatalog = StarCatalog.HIPPARCOS,
        style: ObjectStyle = None,
        rasterize: bool = False,
        size_fn: Callable[[Star], float] = callables.size_by_magnitude,
        alpha_fn: Callable[[Star], float] = callables.alpha_by_magnitude,
        color_fn: Callable[[Star], str] = None,
        where: list = None,
        where_labels: list = None,
        labels: Mapping[int, str] = STAR_NAMES,
        legend_label: str = "Star",
        bayer_labels: bool = False,
        *args,
        **kwargs,
    ):
        """
        Plots stars

        Args:
            mag: Limiting magnitude of stars to plot
            catalog: The catalog of stars to use
            style: If `None`, then the plot's style for stars will be used
            rasterize: If True, then the stars will be rasterized when plotted, which can speed up exporting to SVG and reduce the file size but with a loss of image quality
            size_fn: Callable for calculating the marker size of each star. If `None`, then the marker style's size will be used.
            alpha_fn: Callable for calculating the alpha value (aka "opacity") of each star. If `None`, then the marker style's alpha will be used.
            color_fn: Callable for calculating the color of each star. If `None`, then the marker style's color will be used.
            where: A list of expressions that determine which stars to plot. See [Selecting Objects](/reference-selecting-objects/) for details.
            where_labels: A list of expressions that determine which stars are labeled on the plot. See [Selecting Objects](/reference-selecting-objects/) for details.
            labels: A dictionary that maps a star's HIP id to the label that'll be plotted for that star. If you want to hide name labels, then set this arg to `None`.
            legend_label: Label for stars in the legend. If `None`, then they will not be in the legend.
            bayer_labels: If True, then Bayer labels for stars will be plotted. Set this to False if you want to hide Bayer labels.
        """
        # optic_star_multiplier = 0.57 * (self.FIELD_OF_VIEW_MAX / self.optic.true_fov)

        # def size_fn_mx(st: Star) -> float:
        #     return size_fn(st) * optic_star_multiplier

        super().stars(
            mag=mag,
            catalog=catalog,
            style=style,
            rasterize=rasterize,
            size_fn=size_fn,
            alpha_fn=alpha_fn,
            color_fn=color_fn,
            where=where,
            where_labels=where_labels,
            labels=labels,
            legend_label=legend_label,
            bayer_labels=bayer_labels,
            *args,
            **kwargs,
        )

    def _plot_border(self):
        # since we're using AzimuthalEquidistant projection, the center will always be (0, 0)
        x = 0
        y = 0

        # Background of Viewable Area
        self._background_clip_path = self.optic.patch(
            x,
            y,
            facecolor=self.style.background_color.as_hex(),
            linewidth=0,
            fill=True,
            zorder=ZOrderEnum.LAYER_1,
        )
        self.ax.add_patch(self._background_clip_path)

        # Inner Border
        inner_border = self.optic.patch(
            x,
            y,
            linewidth=2 * self.scale,
            edgecolor=self.style.border_line_color.as_hex(),
            fill=False,
            zorder=ZOrderEnum.LAYER_5 + 100,
        )
        self.ax.add_patch(inner_border)

        # Outer border
        outer_border = self.optic.patch(
            x,
            y,
            padding=0.05,
            linewidth=20 * self.scale,
            edgecolor=self.style.border_bg_color.as_hex(),
            fill=False,
            zorder=ZOrderEnum.LAYER_5,
        )
        self.ax.add_patch(outer_border)

    def _fit_to_ax(self) -> None:
        bbox = self.ax.get_window_extent().transformed(
            self.fig.dpi_scale_trans.inverted()
        )
        width, height = bbox.width, bbox.height
        self.fig.set_size_inches(width, height)

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
            self.az[1] * 1.2,
            self.alt[0],
            self.alt[1],
        ]
        print(bounds)

        self.ax.set_extent(bounds, crs=ccrs.PlateCarree())
        self.ax.gridlines()

        # self._plot_border()
        self._fit_to_ax()

        # self.ax.set_xlim(-1.06 * self.optic.xlim, 1.06 * self.optic.xlim)
        # self.ax.set_ylim(-1.06 * self.optic.ylim, 1.06 * self.optic.ylim)
        # self.optic.transform(self.ax)
