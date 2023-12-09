from abc import ABC, abstractmethod 
from datetime import datetime

from matplotlib import pyplot as plt
from matplotlib import patches

from skyfield.api import Star, wgs84
from skyfield.positionlib import position_of_radec

from starplot.base import StarPlot
from starplot.data import load, stars
from starplot.styles import PlotStyle, ZENITH_BASE
from starplot.utils import in_circle, bv_to_hex_color, azimuth_to_string

"""
Scope:
    scope_focal_length: float,
    eyepiece_focal_length: float,
    eyepiece_fov: float,

Binoculars:
    magnification
    fov

Camera:
    sensor_size_height
    sensor_size_width
    lens_focal_length

    
Methods:
    create patch (for viewbox)
    fov dimensions
"""


class Optic(ABC):
    def __init__(self) -> None:
        pass
    
    @abstractmethod
    def patch(self, center_x, center_y) -> patches.Patch:
        pass

    @abstractmethod
    def transform(self, axis) -> None:
        pass


class Scope(Optic):
    def __init__(self, focal_length: float, eyepiece_focal_length: float, eyepiece_fov: float) -> None:
        self.focal_length = focal_length
        self.eyepiece_focal_length = eyepiece_focal_length
        self.eyepiece_fov = eyepiece_fov
        self.magnification = self.focal_length / self.eyepiece_focal_length
        self.true_fov = self.eyepiece_fov / self.magnification
    
    def patch(self, center_x, center_y, **kwargs):
        return patches.Ellipse(
            (center_x, center_y),
            self.true_fov * 2,
            self.true_fov,
            **kwargs,
        )

class Refractor(Scope):
    def transform(self, axis) -> None:
        axis.invert_xaxis()

class Reflector(Scope):
    def transform(self, axis) -> None:
        axis.invert_yaxis()

class Binoculars(Optic):
    def __init__(self, magnification: float, fov: float) -> None:
        self.magnification = magnification
        self.apparent_fov = fov
        self.true_fov = self.apparent_fov / self.magnification
    
    def patch(self, center_x, center_y, **kwargs):
        return patches.Ellipse(
            (center_x, center_y),
            self.true_fov * 2,
            self.true_fov,
            **kwargs,
        )



class OpticPlot(StarPlot):
    """Creates a new optic plot.

    Args:
        ra: Right ascension of target center
        dec: Declination of target center
        lat: Latitude of viewing location
        lon: Longitude of viewing location
        include_info_text: If True, then the plot will include the time/location
        dt: Date/time to use for star/planet positions (*must be timezone-aware*). Default = current UTC time.
        limiting_magnitude: Limiting magnitude of stars to plot
        limiting_magnitude_labels: Limiting magnitude of stars to label on the plot
        ephemeris: Ephemeris to use for calculating star positions
        style: Styling for the plot (colors, sizes, fonts, etc)
        resolution: Size (in pixels) of largest dimension of the map
        hide_colliding_labels: If True, then labels will not be plotted if they collide with another existing label
        adjust_text: If True, then the labels will be adjusted to avoid overlapping
        colorize_stars: If True, then stars will be filled with their BV color index
        raise_on_below_horizon: If True, then a ValueError will be raised if the target is below the horizon at the specified time/location

    Returns:
        OpticPlot: A new instance of a OpticPlot

    """

    def __init__(
        self,
        ra: float,
        dec: float,
        lat: float,
        lon: float,
        scope_focal_length: float,
        eyepiece_focal_length: float,
        eyepiece_fov: float,
        include_info_text: bool = False,
        dt: datetime = None,
        limiting_magnitude: float = 6.0,
        limiting_magnitude_labels: float = 2.1,
        ephemeris: str = "de421_2001.bsp",
        style: PlotStyle = ZENITH_BASE,
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

        self.scope_focal_length = scope_focal_length
        self.eyepiece_focal_length = eyepiece_focal_length
        self.eyepiece_fov = eyepiece_fov
        self.magnification = scope_focal_length / eyepiece_focal_length
        self.fov = eyepiece_fov / self.magnification

        self._calc_position()
        self._init_plot()

    def in_bounds(self, ra, dec) -> bool:
        x, y = self._prepare_coords(ra, dec)
        result = in_circle(x, y)
        return result

    def _prepare_coords(self, ra, dec) -> (float, float):
        return self.project_fn(position_of_radec(ra, dec))

    def _calc_position(self):
        eph = load(self.ephemeris)
        earth = eph["earth"]

        self.location = earth + wgs84.latlon(self.lat, self.lon)
        self.star = Star(ra_hours=self.ra, dec_degrees=self.dec)
        self.position = self.location.at(self.timescale).observe(self.star)

        self.pos_apparent = self.position.apparent()
        self.pos_alt, self.pos_az, _ = self.pos_apparent.altaz()

        if self.pos_alt.degrees < 0 and self.raise_on_below_horizon:
            raise ValueError("Target is below horizon at specified time/location.")

    def _plot_stars(self):
        stardata = stars.load(
            catalog=stars.StarCatalog.TYCHO_1,
            limiting_magnitude=self.limiting_magnitude,
        )
        self._stardata = stardata
        nearby_stars_df = stardata[
            (stardata["magnitude"] <= self.limiting_magnitude)
            & (stardata["ra_hours"] < self.ra + self.fov / 15 * 1.25)
            & (stardata["ra_hours"] > self.ra - self.fov / 15 * 1.25)
            & (stardata["dec_degrees"] < self.dec + self.fov * 1.25)
            & (stardata["dec_degrees"] > self.dec - self.fov * 1.25)
        ]
        x = []
        y = []
        sizes = []
        alphas = []
        colors = []

        for _, star in nearby_stars_df.iterrows():
            m = star["magnitude"]

            if m < 1.6:
                sizes.append((9 - m) ** 3.56 * self._size_multiplier)
                alphas.append(1)
            elif m < 4.6:
                sizes.append((8 - m) ** 3.4 * self._size_multiplier)
                alphas.append(1)
            elif m < 5.85:
                sizes.append((9 - m) ** 3.26 * self._size_multiplier)
                alphas.append(0.94)
            elif m < 9:
                sizes.append((13 - m) ** 1.46 * self._size_multiplier)
                alphas.append(0.88)
            else:
                sizes.append(3.68 * self._size_multiplier)
                alphas.append((16 - m) * 0.09)

            if self.colorize_stars:
                c = bv_to_hex_color(star["bv"]) or self.style.star.marker.color.as_hex()
            else:
                c = self.style.star.marker.color.as_hex()

            colors.append(c)

            s = Star(ra_hours=star["ra_hours"], dec_degrees=star["dec_degrees"])
            pos = self.location.at(self.timescale).observe(s)
            app = pos.apparent()
            alt, az, _ = app.altaz()
            if self.pos_az.degrees > 350 and az.degrees < 100:
                x.append(az.degrees + 360)
            elif self.pos_az.degrees < 100 and az.degrees > 300:
                x.append(az.degrees - 360)
            else:
                x.append(az.degrees)
            y.append(alt.degrees)

        # Draw stars
        if self.style.star.marker.visible:
            self._plotted_stars = self.ax.scatter(
                x,
                y,
                sizes,
                colors,
                # color=self.style.star.marker.color.as_hex(),
                clip_path=self.background_circle,
                alpha=alphas,
                edgecolors="none",
            )

    def _plot_border(self):
        # Plot border text
        radius = self.fov
        border_font_kwargs = dict(
            fontsize=self.style.border_font_size * self._size_multiplier * 2,
            weight=self.style.border_font_weight,
            color=self.style.border_font_color.as_hex(),
        )
        # self.ax.text(0, 1.009, "N", **border_font_kwargs)
        # self.ax.text(1.003, 0, "W", **border_font_kwargs)
        # self.ax.text(-1.042, 0, "E", **border_font_kwargs)
        # self.ax.text(0, -1.045, "S", **border_font_kwargs)

        # Background Circle
        self.background_circle = patches.Ellipse(
            (self.pos_az.degrees, self.pos_alt.degrees),
            radius * 2,
            radius,
            facecolor=self.style.background_color.as_hex(),
            linewidth=0,
            fill=True,
            zorder=-100,
        )
        self.ax.add_patch(self.background_circle)

        # Inner Border
        inner_border = patches.Ellipse(
            (self.pos_az.degrees, self.pos_alt.degrees),
            radius * 2,
            radius,
            linewidth=2 * self._size_multiplier,
            edgecolor=self.style.border_line_color.as_hex(),
            fill=False,
            zorder=100,
        )
        self.ax.add_patch(inner_border)

        # Outer border circle
        outer_border = patches.Ellipse(
            (self.pos_az.degrees, self.pos_alt.degrees),
            radius * 2 + 0.2,
            radius + 0.1,
            facecolor=self.style.border_bg_color.as_hex(),
            linewidth=4 * self._size_multiplier,
            edgecolor=self.style.border_line_color.as_hex(),
            fill=True,
            zorder=-1024,
        )
        self.ax.add_patch(outer_border)

    def _init_plot(self):
        self.fig = plt.figure(figsize=(self.figure_size, self.figure_size))
        self.ax = plt.axes()

        x = self.pos_az.degrees
        y = self.pos_alt.degrees

        self.ax.set_xlim(x - self.fov * 1.1, x + self.fov * 1.1)
        self.ax.set_ylim(y - self.fov / 2 * 1.06, y + self.fov / 2 * 1.06)
        self.ax.xaxis.set_visible(False)
        self.ax.yaxis.set_visible(False)
        self.ax.set_aspect(2.0)
        self.ax.axis("off")

        self._plot_border()
        self._plot_stars()

        if self.include_info_text:
            self.ax.set_ylim(y - self.fov / 2 * 1.1, y + self.fov / 2 * 1.08)

            dt_str = self.dt.strftime("%m/%d/%Y @ %H:%M:%S") + " " + self.dt.tzname()
            font_size = self.style.legend.font_size * self._size_multiplier * 2.16

            # target, scope, location
            column_labels = [
                "Target (Alt/Az)",
                "Target (RA/DEC)",
                "Observer Lat, Lon",
                "Observer Date/Time",
                "Optic",
            ]
            values = [
                f"{self.pos_alt.degrees:.0f}\N{DEGREE SIGN} / {self.pos_az.degrees:.0f}\N{DEGREE SIGN} ({azimuth_to_string(self.pos_az.degrees)})",
                f"{self.ra:.2f}h / {self.dec:.2f}\N{DEGREE SIGN}",
                f"{self.lat:.2f}\N{DEGREE SIGN}, {self.lon:.2f}\N{DEGREE SIGN}",
                dt_str,
                f"{self.scope_focal_length}mm w/ {self.eyepiece_focal_length}mm ({self.magnification:.0f}x) @  {self.eyepiece_fov:.0f}\N{DEGREE SIGN} = {self.fov:.2f}\N{DEGREE SIGN} TFOV",
            ]

            total_chars = sum([len(v) for v in values])
            widths = [len(v) / total_chars for v in values]
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
            table.scale(1, 2.1)
            for col in range(len(values)):
                table[0, col].set_text_props(
                    fontweight="heavy", fontsize=font_size * 1.15
                )

        # self.ax.invert_xaxis()
