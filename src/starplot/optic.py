import math

from abc import ABC, abstractmethod
from datetime import datetime

from matplotlib import pyplot as plt
from matplotlib import patches

from skyfield.api import Star, wgs84

from starplot.base import StarPlot
from starplot.data import load, stars
from starplot.styles import PlotStyle, ZENITH_BASE
from starplot.utils import bv_to_hex_color, azimuth_to_string


class Optic(ABC):
    def __init__(self) -> None:
        pass

    def __str__(self):
        return "Optic"

    @property
    @abstractmethod
    def xlim(self):
        pass

    @property
    @abstractmethod
    def ylim(self):
        pass

    @property
    @abstractmethod
    def label(self):
        return "Generic"

    @abstractmethod
    def patch(self, center_x, center_y) -> patches.Patch:
        pass

    def transform(self, axis) -> None:
        pass


class Scope(Optic):
    """Scope

    Not meant to be used directly, use subclasses instead (Refractor, Reflector, etc)
    """

    def __init__(
        self, focal_length: float, eyepiece_focal_length: float, eyepiece_fov: float
    ) -> None:
        self.focal_length = focal_length
        self.eyepiece_focal_length = eyepiece_focal_length
        self.eyepiece_fov = eyepiece_fov
        self.magnification = self.focal_length / self.eyepiece_focal_length
        self.true_fov = self.eyepiece_fov / self.magnification

    def __str__(self):
        return f"{self.focal_length}mm w/ {self.eyepiece_focal_length}mm ({self.magnification:.0f}x) @  {self.eyepiece_fov:.0f}\N{DEGREE SIGN} = {self.true_fov:.2f}\N{DEGREE SIGN} TFOV"

    @property
    def xlim(self):
        return self.true_fov * 1.1

    @property
    def ylim(self):
        return self.true_fov / 2 * 1.08

    @property
    def label(self):
        return "Scope"

    def patch(self, center_x, center_y, **kwargs):
        padding = kwargs.pop("padding", 0)
        return patches.Ellipse(
            (center_x, center_y),
            (self.true_fov + padding) * 2,
            self.true_fov + padding,
            **kwargs,
        )


class Refractor(Scope):
    @property
    def label(self):
        return "Refractor"

    def transform(self, axis) -> None:
        axis.invert_xaxis()


class Reflector(Scope):
    @property
    def label(self):
        return "Reflector"

    def transform(self, axis) -> None:
        axis.invert_yaxis()


class Binoculars(Optic):
    """Creates a new Binoculars optic

    Args:
        magnification: Magnification of the binoculars
        fov: Apparent field of view (FOV) of the binoculars in degrees (usually around 64)

    Returns:
        Binoculars: A new instance of a Binoculars optic

    """

    def __init__(self, magnification: float, fov: float) -> None:
        self.magnification = magnification
        self.apparent_fov = fov
        self.true_fov = self.apparent_fov / self.magnification

    def __str__(self):
        return f"{self.magnification}x @ {self.apparent_fov}\N{DEGREE SIGN} = {self.true_fov}\N{DEGREE SIGN}"

    @property
    def xlim(self):
        return self.true_fov * 1.1

    @property
    def ylim(self):
        return self.true_fov / 2 * 1.08

    @property
    def label(self):
        return "Binoculars"

    def patch(self, center_x, center_y, **kwargs):
        padding = kwargs.pop("padding", 0)
        return patches.Ellipse(
            (center_x, center_y),
            (self.true_fov + padding) * 2,
            self.true_fov + padding,
            **kwargs,
        )


class Camera(Optic):
    """Creates a new Binoculars optic

    Note:
        Field of view is calculated using the following formula:

        ```
        TFOV = 2 * arctan( d / (2 * f) )
        ```

        _Where_:

        d = sensor size

        f = focal length of lens

    Args:
        sensor_height: Height of camera sensor (mm)
        sensor_width: Width of camera sensor (mm)
        lens_focal_length: Focal length of camera lens (mm)

    Returns:
        Camera: A new instance of a Camera optic

    """

    def __init__(
        self, sensor_height: float, sensor_width: float, lens_focal_length: float
    ) -> None:
        self.sensor_height = sensor_height
        self.sensor_width = sensor_width
        self.lens_focal_length = lens_focal_length

        self.true_fov_x = 2 * math.degrees(
            math.atan(self.sensor_width / (2 * self.lens_focal_length))
        )
        self.true_fov_y = 2 * math.degrees(
            math.atan(self.sensor_height / (2 * self.lens_focal_length))
        )
        self.true_fov = max(self.true_fov_x, self.true_fov_y)

    def __str__(self):
        return f"{self.sensor_width}x{self.sensor_height} w/ {self.lens_focal_length}mm lens = {self.true_fov_x:.2f}\N{DEGREE SIGN} x {self.true_fov_y:.2f}\N{DEGREE SIGN}"

    @property
    def xlim(self):
        return self.true_fov_x * 1.2

    @property
    def ylim(self):
        return self.true_fov_y / 2 * 1.16

    @property
    def label(self):
        return "Camera"

    def patch(self, center_x, center_y, **kwargs):
        # needs to be 2x wider than height
        padding = kwargs.pop("padding", 0)
        x = center_x - self.true_fov_x - padding * 2
        y = center_y - (self.true_fov_y / 2) - padding
        return patches.Rectangle(
            (x, y),
            (self.true_fov_x + padding * 2) * 2,
            self.true_fov_y + padding * 2,
            **kwargs,
        )


class OpticPlot(StarPlot):
    """Creates a new optic plot.

    Args:
        optic: Optic instance that defines optical parameters
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

    FIELD_OF_VIEW_MAX = 8.0

    def __init__(
        self,
        optic: Optic,
        ra: float,
        dec: float,
        lat: float,
        lon: float,
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

        self.optic = optic

        if self.optic.true_fov > self.FIELD_OF_VIEW_MAX:
            raise ValueError(
                f"Field of View too big: {self.optic.true_fov} (max = {self.FIELD_OF_VIEW_MAX})"
            )

        # self._size_multiplier = self._size_multiplier * 2 / self.optic.true_fov
        self._calc_position()
        self._init_plot()

    def _prepare_coords(self, ra, dec) -> (float, float):
        point = Star(ra_hours=ra, dec_degrees=dec)
        position = self.location.at(self.timescale).observe(point)
        pos_apparent = position.apparent()
        pos_alt, pos_az, _ = pos_apparent.altaz()
        return pos_az.degrees, pos_alt.degrees

    def in_bounds(self, ra, dec) -> bool:
        x, y = self._prepare_coords(ra, dec)
        transformed = self.ax.transData.transform((x, y))
        return self.background_patch.contains_point(transformed)

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
            & (stardata["ra_hours"] < self.ra + self.optic.true_fov / 15 * 1.25)
            & (stardata["ra_hours"] > self.ra - self.optic.true_fov / 15 * 1.25)
            & (stardata["dec_degrees"] < self.dec + self.optic.true_fov * 1.25)
            & (stardata["dec_degrees"] > self.dec - self.optic.true_fov * 1.25)
        ]
        x = []
        y = []
        sizes = []
        alphas = []
        colors = []

        for _, star in nearby_stars_df.iterrows():
            m = star["magnitude"]

            if m < 4.6:
                sizes.append((9 - m) ** 3.46 * self._size_multiplier)
                alphas.append(1)
            # elif m < 4.6:
            #     sizes.append((9 - m) ** 3.68 * self._size_multiplier)
            #     alphas.append(1)
            elif m < 5.85:
                sizes.append((9 - m) ** 3.46 * self._size_multiplier)
                alphas.append(0.94)
            elif m < 9:
                sizes.append((13 - m) ** 1.62 * self._size_multiplier)
                alphas.append(0.88)
            else:
                sizes.append(3.72 * self._size_multiplier)
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
                clip_path=self.background_patch,
                alpha=alphas,
                edgecolors="none",
            )
            self._plotted_stars.set_clip_path(self.background_patch)

    def _plot_border(self):
        # Plot border text
        # radius = self.fov
        border_font_kwargs = dict(
            fontsize=self.style.border_font_size * self._size_multiplier * 2,
            weight=self.style.border_font_weight,
            color=self.style.border_font_color.as_hex(),
        )
        # self.ax.text(0, 1.009, "N", **border_font_kwargs)
        # self.ax.text(1.003, 0, "W", **border_font_kwargs)
        # self.ax.text(-1.042, 0, "E", **border_font_kwargs)
        # self.ax.text(0, -1.045, "S", **border_font_kwargs)

        # Background of Viewable Area
        self.background_patch = self.optic.patch(
            self.pos_az.degrees,
            self.pos_alt.degrees,
            facecolor=self.style.background_color.as_hex(),
            linewidth=0,
            fill=True,
            zorder=-100,
        )
        self.ax.add_patch(self.background_patch)

        # Inner Border
        inner_border = self.optic.patch(
            self.pos_az.degrees,
            self.pos_alt.degrees,
            linewidth=2 * self._size_multiplier,
            edgecolor=self.style.border_line_color.as_hex(),
            fill=False,
            zorder=128,
        )
        self.ax.add_patch(inner_border)

        # Outer border
        outer_border = self.optic.patch(
            self.pos_az.degrees,
            self.pos_alt.degrees,
            padding=0.02,
            linewidth=30 * self._size_multiplier,
            edgecolor=self.style.border_bg_color.as_hex(),
            fill=False,
            zorder=64,
        )
        self.ax.add_patch(outer_border)

    def _init_plot(self):
        self.fig = plt.figure(figsize=(self.figure_size, self.figure_size))
        self.ax = plt.axes()

        x = self.pos_az.degrees
        y = self.pos_alt.degrees

        self.ax.set_xlim(x - self.optic.xlim, x + self.optic.xlim)
        self.ax.set_ylim(y - self.optic.ylim, y + self.optic.ylim)
        self.ax.xaxis.set_visible(False)
        self.ax.yaxis.set_visible(False)
        self.ax.set_aspect(2.0)
        self.ax.axis("off")

        self._plot_border()
        self._plot_stars()
        self.optic.transform(self.ax)

        if self.include_info_text:
            self.ax.set_xlim(x - self.optic.xlim * 1.03, x + self.optic.xlim * 1.03)
            self.ax.set_ylim(y - self.optic.ylim * 1.03, y + self.optic.ylim * 1.03)

            dt_str = self.dt.strftime("%m/%d/%Y @ %H:%M:%S") + " " + self.dt.tzname()
            font_size = self.style.legend.font_size * self._size_multiplier * 2.16

            # target, scope, location
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
            table.scale(1, 3.1)
            for col in range(len(values)):
                table[0, col].set_text_props(
                    fontweight="heavy", fontsize=font_size * 1.15
                )
