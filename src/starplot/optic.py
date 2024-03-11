from datetime import datetime
from typing import Callable

import pandas as pd

from cartopy import crs as ccrs
from matplotlib import pyplot as plt, patches, path
from skyfield.api import wgs84, Star as SkyfieldStar

from starplot import callables
from starplot.base import BasePlot
from starplot.data.stars import StarCatalog
from starplot.mixins import ExtentMaskMixin
from starplot.models import Star
from starplot.optics import Optic
from starplot.plotters import StarPlotterMixin, DsoPlotterMixin
from starplot.styles import PlotStyle, MarkerStyle, LabelStyle, extensions, use_style
from starplot.utils import azimuth_to_string

pd.options.mode.chained_assignment = None  # default='warn'

DEFAULT_OPTIC_STYLE = PlotStyle().extend(extensions.OPTIC)


class OpticPlot(BasePlot, ExtentMaskMixin, StarPlotterMixin, DsoPlotterMixin):
    """Creates a new optic plot.

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

    Returns:
        OpticPlot: A new instance of an OpticPlot

    """

    FIELD_OF_VIEW_MAX = 9.0

    def __init__(
        self,
        optic: Optic,
        ra: float,
        dec: float,
        lat: float,
        lon: float,
        dt: datetime = None,
        ephemeris: str = "de421_2001.bsp",
        style: PlotStyle = DEFAULT_OPTIC_STYLE,
        resolution: int = 2048,
        hide_colliding_labels: bool = True,
        raise_on_below_horizon: bool = True,
        *args,
        **kwargs,
    ) -> "OpticPlot":
        super().__init__(
            dt,
            ephemeris,
            style,
            resolution,
            hide_colliding_labels,
            *args,
            **kwargs,
        )
        self.logger.debug("Creating OpticPlot...")
        self.ra = ra
        self.dec = dec
        self.lat = lat
        self.lon = lon
        self.raise_on_below_horizon = raise_on_below_horizon

        self.optic = optic
        self._crs = ccrs.CRS(
            proj4_params=[
                ("proj", "latlong"),
                ("a", "6378137"),
            ],
            globe=ccrs.Globe(ellipse="sphere", flattening=0),
        )
        if self.optic.true_fov > self.FIELD_OF_VIEW_MAX:
            raise ValueError(
                f"Field of View too big: {self.optic.true_fov} (max = {self.FIELD_OF_VIEW_MAX})"
            )
        self._calc_position()
        self._adjust_radec_minmax()
        self._init_plot()

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
        x, y = self._proj.transform_point(az, alt, self._crs)
        return self.optic.in_bounds(x, y, scale)

    def _polygon(self, points, style, **kwargs):
        super()._polygon(points, style, transform=self._crs, **kwargs)

    def _calc_position(self):
        earth = self.ephemeris["earth"]

        self.location = earth + wgs84.latlon(self.lat, self.lon)
        self.star = SkyfieldStar(ra_hours=self.ra, dec_degrees=self.dec)
        self.observe = self.location.at(self.timescale).observe
        self.position = self.observe(self.star)

        self.pos_apparent = self.position.apparent()
        self.pos_alt, self.pos_az, _ = self.pos_apparent.altaz()

        if self.pos_alt.degrees < 0 and self.raise_on_below_horizon:
            raise ValueError("Target is below horizon at specified time/location.")

    def _adjust_radec_minmax(self):
        self.ra_min = self.ra - self.optic.true_fov / 15 * 1.08
        self.ra_max = self.ra + self.optic.true_fov / 15 * 1.08
        self.dec_max = self.dec + self.optic.true_fov / 2 * 1.03
        self.dec_min = self.dec - self.optic.true_fov / 2 * 1.03

        if self.dec > 70 or self.dec < -70:
            # naive method of getting all the stars near the poles
            self.ra_min = 0
            self.ra_max = 24

        self.logger.debug(
            f"Extent = RA ({self.ra_min:.2f}, {self.ra_max:.2f}) DEC ({self.dec_min:.2f}, {self.dec_max:.2f})"
        )

    def _scatter_stars(
        self, ras, decs, sizes, alphas, colors, style=None, epoch_year=None, **kwargs
    ):
        """Override StarPlotterMixin _scatter_stars so we can convert to alt/az coords"""
        ra_hours = [ra / 15 for ra in ras]

        df = pd.DataFrame({"ra_hours": ra_hours, "dec_degrees": decs})
        df["epoch_year"] = epoch_year

        stars_apparent = self.observe(SkyfieldStar.from_dataframe(df)).apparent()
        nearby_stars_alt, nearby_stars_az, _ = stars_apparent.altaz()

        df["alt"], df["az"] = (
            nearby_stars_alt.degrees,
            nearby_stars_az.degrees,
        )

        plotted = super()._scatter_stars(
            df["az"],
            df["alt"],
            sizes,
            alphas,
            colors,
            style,
            **kwargs,
        )
        plotted.set_clip_on(True)

        if type(self._background_clip_path) == patches.Rectangle:
            # convert to generic path to handle possible rotation angle:
            clip_path = path.Path(self._background_clip_path.get_corners())
            plotted.set_clip_path(clip_path, transform=self.ax.transData)
        else:
            plotted.set_clip_path(self._background_clip_path)

    @use_style(MarkerStyle, "star")
    def stars(
        self,
        mag: float = 8.0,
        mag_labels: float = 6.0,
        catalog: StarCatalog = StarCatalog.TYCHO_1,
        style: MarkerStyle = None,
        rasterize: bool = False,
        size_fn: Callable[[Star], float] = callables.size_by_magnitude_for_optic,
        alpha_fn: Callable[[Star], float] = callables.alpha_by_magnitude,
        color_fn: Callable[[Star], str] = None,
        legend_label: str = "Star",
        *args,
        **kwargs,
    ):
        """
        Plots stars

        Args:
            mag: Limiting magnitude of stars to plot
            mag_labels: Limiting magnitude of stars to label on the plot
            catalog: The catalog of stars to use: "hipparcos" or "tycho-1"
            style: If `None`, then the plot's style for stars will be used
            rasterize: If True, then the stars will be rasterized when plotted, which can speed up exporting to SVG and reduce the file size but with a loss of image quality
            size_fn: Callable for calculating the marker size of each star. If `None`, then the marker style's size will be used.
            alpha_fn: Callable for calculating the alpha value (aka "opacity") of each star. If `None`, then the marker style's alpha will be used.
            color_fn: Callable for calculating the color of each star. If `None`, then the marker style's color will be used.
            legend_label: Label for stars in the legend. If `None`, then they will not be in the legend.
        """
        optic_star_multiplier = 0.4 * (self.FIELD_OF_VIEW_MAX / self.optic.true_fov)

        def size_fn_mx(st: Star) -> float:
            return size_fn(st) * optic_star_multiplier

        super().stars(
            mag=mag,
            mag_labels=mag_labels,
            catalog=catalog,
            style=style,
            rasterize=rasterize,
            size_fn=size_fn_mx,
            alpha_fn=alpha_fn,
            color_fn=color_fn,
            legend_label=legend_label,
            *args,
            **kwargs,
        )

    def _plot_text(self, ra: float, dec: float, text: str, *args, **kwargs) -> None:
        super()._plot_text(
            ra, dec, text, clip_path=self._background_clip_path, *args, **kwargs
        )

    @use_style(LabelStyle, "info_text")
    def info(self, style: LabelStyle = None):
        """
        Plots a table with info about the plot, including:

        - Target's position (alt/az and ra/dec)
        - Observer's position (lat/lon and date/time)
        - Optic details (type, magnification, FOV)

        Args:
            style: If `None`, then the plot's style for info text will be used
        """
        self.ax.set_xlim(-1.22 * self.optic.xlim, 1.22 * self.optic.xlim)
        self.ax.set_ylim(-1.12 * self.optic.ylim, 1.12 * self.optic.ylim)
        self.optic.transform(
            self.ax
        )  # apply transform again because new xy limits will undo the transform

        dt_str = self.dt.strftime("%m/%d/%Y @ %H:%M:%S") + " " + self.dt.tzname()
        font_size = style.font_size * self._size_multiplier * 2

        column_labels = [
            "Target (Alt/Az)",
            "Target (RA/DEC)",
            "Observer Lat, Lon",
            "Observer Date/Time",
            f"Optic - {self.optic.label}",
        ]
        values = [
            f"{self.pos_alt.degrees:.0f}\N{DEGREE SIGN} / {self.pos_az.degrees:.0f}\N{DEGREE SIGN} ({azimuth_to_string(self.pos_az.degrees)})",
            f"{self.ra:.2f}h / {self.dec:.2f}\N{DEGREE SIGN}",
            f"{self.lat:.2f}\N{DEGREE SIGN}, {self.lon:.2f}\N{DEGREE SIGN}",
            dt_str,
            str(self.optic),
        ]
        widths = [0.15, 0.15, 0.2, 0.2, 0.3]

        table = self.ax.table(
            cellText=[values],
            cellLoc="center",
            colWidths=widths,
            rowLabels=[None],
            colLabels=column_labels,
            loc="bottom",
            edges="vertical",
        )
        table.auto_set_font_size(False)
        table.set_fontsize(font_size)
        table.scale(1, 3.1)

        # Apply style to all cells
        for row in [0, 1]:
            for col in range(len(values)):
                table[row, col].set_text_props(
                    **style.matplot_kwargs(self._size_multiplier)
                )

        # Apply some styles only to the header row
        for col in range(len(values)):
            table[0, col].set_text_props(fontweight="heavy", fontsize=font_size * 1.15)

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
            zorder=-1000,
        )
        self.ax.add_patch(self._background_clip_path)

        # Inner Border
        inner_border = self.optic.patch(
            x,
            y,
            linewidth=2 * self._size_multiplier,
            edgecolor=self.style.border_line_color.as_hex(),
            fill=False,
            zorder=128,
        )
        self.ax.add_patch(inner_border)

        # Outer border
        outer_border = self.optic.patch(
            x,
            y,
            padding=0.05,
            linewidth=20 * self._size_multiplier,
            edgecolor=self.style.border_bg_color.as_hex(),
            fill=False,
            zorder=64,
        )
        self.ax.add_patch(outer_border)

    def _fit_to_ax(self) -> None:
        bbox = self.ax.get_window_extent().transformed(
            self.fig.dpi_scale_trans.inverted()
        )
        width, height = bbox.width, bbox.height
        self.fig.set_size_inches(width, height)

    def _init_plot(self):
        self._proj = ccrs.AzimuthalEquidistant(
            central_longitude=self.pos_az.degrees,
            central_latitude=self.pos_alt.degrees,
        )
        self._proj.threshold = 1000
        self.fig = plt.figure(
            figsize=(self.figure_size, self.figure_size),
            facecolor=self.style.figure_background_color.as_hex(),
            layout="constrained",
        )
        self.ax = plt.axes(projection=self._proj)
        self.ax.xaxis.set_visible(False)
        self.ax.yaxis.set_visible(False)
        self.ax.axis("off")

        self._plot_border()
        self._fit_to_ax()

        self.ax.set_xlim(-1.06 * self.optic.xlim, 1.06 * self.optic.xlim)
        self.ax.set_ylim(-1.06 * self.optic.ylim, 1.06 * self.optic.ylim)
        self.optic.transform(self.ax)
