from datetime import datetime

from cartopy import crs as ccrs
from matplotlib import pyplot as plt
from skyfield.api import Star, wgs84

from starplot.base import StarPlot
from starplot.data import load, stars, bayer
from starplot.optics import Optic
from starplot.styles import PlotStyle, OPTIC_BASE
from starplot.utils import bv_to_hex_color, azimuth_to_string

import pandas as pd

pd.options.mode.chained_assignment = None  # default='warn'


class OpticPlot(StarPlot):
    """Creates a new optic plot.

    Args:
        optic: Optic instance that defines optical parameters
        ra: Right ascension of target center
        dec: Declination of target center
        lat: Latitude of observer's location
        lon: Longitude of observer's location
        dt: Date/time of observation (*must be timezone-aware*). Default = current UTC time.
        limiting_magnitude: Limiting magnitude of stars to plot
        limiting_magnitude_labels: Limiting magnitude of stars to label on the plot
        include_info_text: If True, then the plot will include a table with details of the target/observer/optic
        ephemeris: Ephemeris to use for calculating planet positions (see [Skyfield's documentation](https://rhodesmill.org/skyfield/planets.html) for details)
        style: Styling for the plot (colors, sizes, fonts, etc)
        resolution: Size (in pixels) of largest dimension of the map
        hide_colliding_labels: If True, then labels will not be plotted if they collide with another existing label
        adjust_text: If True, then the labels will be adjusted to avoid overlapping
        colorize_stars: If True, then stars will be filled with their BV color index
        raise_on_below_horizon: If True, then a ValueError will be raised if the target is below the horizon at the observing time/location

    Returns:
        OpticPlot: A new instance of a OpticPlot

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
        limiting_magnitude: float = 6.0,
        limiting_magnitude_labels: float = 2.1,
        include_info_text: bool = False,
        ephemeris: str = "de421_2001.bsp",
        style: PlotStyle = OPTIC_BASE,
        resolution: int = 2048,
        hide_colliding_labels: bool = True,
        adjust_text: bool = False,
        colorize_stars: bool = False,
        raise_on_below_horizon: bool = True,
        *args,
        **kwargs,
    ) -> "OpticPlot":
        super().__init__(
            dt,
            limiting_magnitude,
            limiting_magnitude_labels,
            ephemeris,
            style,
            resolution,
            hide_colliding_labels,
            adjust_text,
            *args,
            **kwargs,
        )
        self.ra = ra
        self.dec = dec
        self.lat = lat
        self.lon = lon
        self.include_info_text = include_info_text
        self.colorize_stars = colorize_stars
        self.raise_on_below_horizon = raise_on_below_horizon

        self.optic = optic
        self._geodetic = ccrs.Geodetic()

        if self.optic.true_fov > self.FIELD_OF_VIEW_MAX:
            raise ValueError(
                f"Field of View too big: {self.optic.true_fov} (max = {self.FIELD_OF_VIEW_MAX})"
            )

        self._star_size_multiplier = (
            self._size_multiplier * 0.4 * (self.FIELD_OF_VIEW_MAX / self.optic.true_fov)
        )
        self._calc_position()
        self._init_plot()

    def _prepare_coords(self, ra, dec) -> (float, float):
        """Converts RA/DEC to AZ/ALT"""
        point = Star(ra_hours=ra, dec_degrees=dec)
        position = self.observe(point)
        pos_apparent = position.apparent()
        pos_alt, pos_az, _ = pos_apparent.altaz()
        return pos_az.degrees, pos_alt.degrees

    def _plot_kwargs(self) -> dict:
        return dict(transform=self._geodetic)

    def in_bounds(self, ra, dec) -> bool:
        az, alt = self._prepare_coords(ra, dec)
        return self.in_bounds_altaz(alt, az)

    def in_bounds_altaz(self, alt, az, scale: float = 1) -> bool:
        x, y = self._proj.transform_point(az, alt, self._geodetic)
        return self.optic.in_bounds(x, y, scale)

    def _calc_position(self):
        eph = load(self.ephemeris)
        earth = eph["earth"]

        self.location = earth + wgs84.latlon(self.lat, self.lon)
        self.star = Star(ra_hours=self.ra, dec_degrees=self.dec)
        self.observe = self.location.at(self.timescale).observe
        self.position = self.observe(self.star)

        self.pos_apparent = self.position.apparent()
        self.pos_alt, self.pos_az, _ = self.pos_apparent.altaz()

        if self.pos_alt.degrees < 0 and self.raise_on_below_horizon:
            raise ValueError("Target is below horizon at specified time/location.")

    def _plot_stars(self):
        stardata = stars.load(stars.StarCatalog.TYCHO_1)
        self._stardata = stardata

        ra_min = self.ra - self.optic.true_fov / 15 * 1.08
        ra_max = self.ra + self.optic.true_fov / 15 * 1.08

        if self.dec > 70 or self.dec < -70:
            # naive method of getting all the stars near the poles
            ra_min = 0
            ra_max = 24

        nearby_stars_df = stardata[
            (stardata["magnitude"] <= self.limiting_magnitude)
            & (stardata["ra_hours"] < ra_max)
            & (stardata["ra_hours"] > ra_min)
            & (stardata["dec_degrees"] < self.dec + self.optic.true_fov / 2 * 1.03)
            & (stardata["dec_degrees"] > self.dec - self.optic.true_fov / 2 * 1.03)
        ]
        x = []
        y = []
        sizes = []
        alphas = []
        colors = []

        # calculate apparent position (alt/az) of stars
        stars_apparent = self.observe(Star.from_dataframe(nearby_stars_df)).apparent()
        nearby_stars_alt, nearby_stars_az, _ = stars_apparent.altaz()
        nearby_stars_df["alt"], nearby_stars_df["az"] = (
            nearby_stars_alt.degrees,
            nearby_stars_az.degrees,
        )

        for _, star in nearby_stars_df.iterrows():
            m = star["magnitude"]
            alt, az = star["alt"], star["az"]

            if not self.in_bounds_altaz(alt, az):
                continue

            if m < 4.6:
                sizes.append((9 - m) ** 3.34 * self._star_size_multiplier)
                alphas.append(1)
            # elif m < 4.6:
            #     sizes.append((9 - m) ** 3.68 * self._size_multiplier)
            #     alphas.append(1)
            elif m < 5.85:
                sizes.append((9 - m) ** 3.46 * self._star_size_multiplier)
                alphas.append(0.94)
            elif m < 9:
                sizes.append((13 - m) ** 1.62 * self._star_size_multiplier)
                alphas.append(0.88)
            else:
                sizes.append(3.72 * self._star_size_multiplier)
                alphas.append((16 - m) * 0.09)

            if self.colorize_stars:
                c = bv_to_hex_color(star["bv"]) or self.style.star.marker.color.as_hex()
            else:
                c = self.style.star.marker.color.as_hex()

            colors.append(c)
            x.append(az)
            y.append(alt)

        # Draw stars
        if self.style.star.marker.visible:
            self._plotted_stars = self.ax.scatter(
                x,
                y,
                sizes,
                colors,
                clip_path=self.background_patch,
                alpha=alphas,
                edgecolors="none",
                **self._plot_kwargs(),
            )
            self._plotted_stars.set_clip_path(self.background_patch)
            self._add_legend_handle_marker("Star", self.style.star.marker)

        # Plot star labels (names and bayer designations)
        stars_labeled = nearby_stars_df[
            (nearby_stars_df["magnitude"] <= self.limiting_magnitude_labels)
        ]

        stars_labeled.sort_values("magnitude")

        for hip_id, s in stars_labeled.iterrows():
            name = stars.hip_names.get(hip_id)
            bayer_desig = bayer.hip.get(hip_id)
            ra, dec = s["ra_hours"], s["dec_degrees"]
            alt, az = s["alt"], s["az"]

            if not self.in_bounds_altaz(alt, az, scale=0.9):
                continue

            if name and self.style.star.label.visible:
                style = self.style.star.label.matplot_kwargs(self._size_multiplier)
                self._plot_text(ra, dec, name, ha="left", va="top", **style)

            if bayer_desig and self.style.bayer_labels.visible:
                style = self.style.bayer_labels.matplot_kwargs(self._size_multiplier)
                self._plot_text(ra, dec, bayer_desig, ha="right", va="bottom", **style)

    def _plot_info(self):
        if not self.include_info_text:
            return

        self.ax.set_xlim(-1.22 * self.optic.xlim, 1.22 * self.optic.xlim)
        self.ax.set_ylim(-1.12 * self.optic.ylim, 1.12 * self.optic.ylim)

        dt_str = self.dt.strftime("%m/%d/%Y @ %H:%M:%S") + " " + self.dt.tzname()
        font_size = self.style.info_text.font_size * self._size_multiplier * 2

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
                    **self.style.info_text.matplot_kwargs(self._size_multiplier)
                )

        # Apply some styles only to the header row
        for col in range(len(values)):
            table[0, col].set_text_props(fontweight="heavy", fontsize=font_size * 1.15)

    def _plot_border(self):
        x, y = self._proj.transform_point(
            self.pos_az.degrees, self.pos_alt.degrees, self._geodetic
        )

        # Background of Viewable Area
        self.background_patch = self.optic.patch(
            x,
            y,
            facecolor=self.style.background_color.as_hex(),
            linewidth=0,
            fill=True,
            zorder=-100,
        )
        self.ax.add_patch(self.background_patch)

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
        self._proj.threshold = 100

        self.fig = plt.figure(
            figsize=(self.figure_size, self.figure_size),
            # facecolor=self.style.background_color.as_hex(),
            layout="tight",
        )
        self.ax = plt.axes(projection=self._proj)

        self.ax.xaxis.set_visible(False)
        self.ax.yaxis.set_visible(False)
        self.ax.axis("off")

        self._plot_border()
        self._plot_stars()
        self._plot_planets()
        self._plot_moon()

        self._fit_to_ax()

        self.ax.set_xlim(-1.03 * self.optic.xlim, 1.03 * self.optic.xlim)
        self.ax.set_ylim(-1.03 * self.optic.ylim, 1.03 * self.optic.ylim)

        self._plot_info()

        self.optic.transform(self.ax)

        self.refresh_legend()

        if self.adjust_text:
            self.adjust_labels()
