from typing import Callable

import pandas as pd

from skyfield.api import Star as SkyfieldStar

from pyproj import CRS, Transformer
from starplot import callables, geometry
from starplot.coordinates import CoordinateSystem

from starplot.data.catalogs import Catalog, BIG_SKY_MAG11
from starplot.mixins import ExtentMaskMixin
from starplot.models import Star, Optic, Camera
from starplot.models.observer import Observer
from starplot.projections import EquidistantOptic
from starplot.styles import (
    PlotStyle,
    ObjectStyle,
    LabelStyle,
    extensions,
    use_style,
    ZOrderEnum,
    GradientDirection,
    PolygonStyle,
)
from starplot.utils import azimuth_to_string

from starplot.svg.base import BasePlot
from starplot.svg.dsos import DsoPlotterMixin
from starplot.svg.text import TextPlotterMixin, CollisionHandler


"""

TODO:

    - info function
    - invert x/y
    - testing
    - make border plot in figure coordinates

"""


class OpticPlot(
    BasePlot,
    ExtentMaskMixin,
    # StarPlotterMixin,
    DsoPlotterMixin,
    TextPlotterMixin,
    # LegendPlotterMixin,
):
    """Creates a new optic plot.

    Args:
        ra: Right ascension of target center, in degrees (0...360)
        dec: Declination of target center, in degrees (-90...90)
        optic: Optic instance that defines optical parameters
        observer: Observer instance which specifies a time and place. Defaults to `Observer()`
        ephemeris: Ephemeris to use for calculating planet positions (see [Skyfield's documentation](https://rhodesmill.org/skyfield/planets.html) for details)
        style: Styling for the plot (colors, sizes, fonts, etc). If `None`, it defaults to `PlotStyle()`
        resolution: Size (in pixels) of largest dimension of the map
        point_label_handler: Default [CollisionHandler][starplot.CollisionHandler] for point labels.
        area_label_handler: Default [CollisionHandler][starplot.CollisionHandler] for area labels.
        path_label_handler: Default [CollisionHandler][starplot.CollisionHandler] for path labels.
        raise_on_below_horizon: If True, then a ValueError will be raised if the target is below the horizon at the observing time/location
        scale: Scaling factor that will be applied to all sizes in styles (e.g. font size, marker size, line widths, etc). For example, if you want to make everything 2x bigger, then set the scale to 2. At `scale=1` and `resolution=4096` (the default), all sizes are optimized visually for a map that covers 1-3 constellations. So, if you're creating a plot of a _larger_ extent, then it'd probably be good to decrease the scale (i.e. make everything smaller) -- and _increase_ the scale if you're plotting a very small area.
        autoscale: If True, then the scale will be set automatically based on resolution.
        suppress_warnings: If True (the default), then all warnings will be suppressed

    Returns:
        OpticPlot: A new instance of an OpticPlot

    """

    FIELD_OF_VIEW_MAX = 20

    def __init__(
        self,
        ra: float,
        dec: float,
        optic: Optic,
        observer: Observer = None,
        ephemeris: str = "de421.bsp",
        style: PlotStyle = None,
        resolution: int = 4096,
        point_label_handler: CollisionHandler = None,
        area_label_handler: CollisionHandler = None,
        path_label_handler: CollisionHandler = None,
        raise_on_below_horizon: bool = True,
        scale: float = 1.0,
        autoscale: bool = False,
        suppress_warnings: bool = True,
        *args,
        **kwargs,
    ) -> "OpticPlot":
        observer = observer or Observer()
        style = style or PlotStyle().extend(extensions.OPTIC)

        if isinstance(optic, Camera) and style.has_gradient_background():
            raise ValueError("Gradient backgrounds are not yet supported for cameras.")

        self.ra = ra
        self.dec = dec
        self.raise_on_below_horizon = raise_on_below_horizon
        self.optic = optic
        self.observer = observer

        self.ephemeris_name = ephemeris
        # self.ephemeris = load(ephemeris)
        # self.earth = self.ephemeris["earth"]

        self._calc_position()

        projection = EquidistantOptic(center_ra=self.pos_az, center_dec=self.pos_alt)
        clip_path = self.optic.polygon(self.pos_az, self.pos_alt)

        super().__init__(
            observer,
            ephemeris,
            style,
            resolution,
            point_label_handler=point_label_handler,
            area_label_handler=area_label_handler,
            path_label_handler=path_label_handler,
            scale=scale,
            autoscale=autoscale,
            suppress_warnings=suppress_warnings,
            projection=projection,
            bounds=clip_path.bounds,
            invert_x=optic.invert_x,
            invert_y=optic.invert_y,
            clip_path=clip_path,
            crs=CRS.from_proj4("+proj=latlon +ellps=sphere +a=6378137"),
            *args,
            **kwargs,
        )

        self.logger.debug("Creating OpticPlot...")

        if self.optic.true_fov > self.FIELD_OF_VIEW_MAX:
            raise ValueError(
                f"Field of View too big: {self.optic.true_fov} (max = {self.FIELD_OF_VIEW_MAX}). Tip: Use horizon or map plots for wider fields of view."
            )

        self._adjust_radec_minmax()
        self._plot_border()

    @property
    def alt(self):
        """Altitude of target (degrees)"""
        return self.pos_alt

    @property
    def az(self):
        """Azimuth of target (degrees)"""
        return self.pos_az

    def _prepare_coords(self, ra, dec) -> (float, float):
        """Converts RA/DEC to AZ/ALT"""
        return self.observer._apparent(
            obj=SkyfieldStar(ra_hours=ra / 15, dec_degrees=dec),
            ephemeris=self.ephemeris_name,
        )

    def _prepare_coords_many(
        self, coordinates: list, epoch_year: float = 2000
    ) -> (float, float):
        """Converts RA/DEC to AZ/ALT"""
        df = pd.DataFrame(coordinates, columns=["ra", "dec"])
        df["ra_hours"], df["dec_degrees"] = (df.ra / 15, df.dec)
        df["epoch_year"] = epoch_year

        sf_star = SkyfieldStar.from_dataframe(df)

        df["x"], df["y"] = self.observer._apparent(
            obj=sf_star,
            ephemeris=self.ephemeris_name,
        )

        return list(zip(df["x"], df["y"]))

    def _plot_kwargs(self) -> dict:
        return dict(transform=self._crs)

    def in_bounds(self, ra, dec) -> bool:
        """Determine if a coordinate is within the bounds of the plot.

        Args:
            ra: Right ascension, in degrees (0...360)
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
        x_axes, y_axes = self.canvas._to_axes(az, alt)
        return 0 <= x_axes <= 1 and 0 <= y_axes <= 1

    def _calc_position(self):
        self.observe = self.observer.observe(self.ephemeris_name)

        target = SkyfieldStar(ra_hours=self.ra / 15, dec_degrees=self.dec)
        self.pos_az, self.pos_alt = self.observer._apparent(
            obj=target,
            ephemeris=self.ephemeris_name,
        )
        if self.pos_alt < 0 and self.raise_on_below_horizon:
            raise ValueError("Target is below horizon at specified time/location.")

    def _adjust_radec_minmax(self):
        fov = self.optic.true_fov
        extent = geometry.rectangle(
            center=(self.ra, self.dec),
            height_degrees=fov,
            width_degrees=fov,
        )
        minx, miny, maxx, maxy = extent.bounds
        self.ra_min = minx
        self.ra_max = maxx
        self.dec_min = miny
        self.dec_max = maxy

        if self.ra_max < 0:
            self.ra_max += 360
        if self.ra_min < 0:
            self.ra_min += 360

        # handle wrapping
        if self.ra_max < self.ra_min:
            self.ra_max += 360

        if self.dec > self.dec_max:
            self.dec_max = 90
            self.ra_min = 0
            self.ra_max = 360

        if self.dec < self.dec_min:
            self.dec_min = -90
            self.ra_min = 0
            self.ra_max = 360

        self.logger.debug(
            f"Extent = RA ({self.ra_min:.2f}, {self.ra_max:.2f}) DEC ({self.dec_min:.2f}, {self.dec_max:.2f})"
        )

    def _in_bounds_xy(self, x: float, y: float) -> bool:
        return self.in_bounds_altaz(y, x)  # alt = y, az = x

    def _prepare_star_coords(self, df):
        df["x"], df["y"] = self.observer._apparent(
            obj=SkyfieldStar.from_dataframe(df),
            ephemeris=self.ephemeris_name,
        )
        return df

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
        self.ax.set_ylim(-1.1 * self.optic.ylim, 1.1 * self.optic.ylim)
        self.optic.transform(
            self.ax
        )  # apply transform again because new xy limits will undo the transform

        dt_str = (
            self.observer.dt.strftime("%m/%d/%Y @ %H:%M:%S")
            + " "
            + self.observer.dt.tzname()
        )
        font_size = style.font_size * self.scale

        column_labels = [
            "Target (Alt/Az)",
            "Target (RA/DEC)",
            "Observer Lat, Lon",
            "Observer Date/Time",
            f"Optic - {self.optic.label}",
        ]
        values = [
            f"{self.pos_alt:.0f}\N{DEGREE SIGN} / {self.pos_az:.0f}\N{DEGREE SIGN} ({azimuth_to_string(self.pos_az)})",
            f"{(self.ra / 15):.2f}h / {self.dec:.2f}\N{DEGREE SIGN}",
            f"{self.observer.lat:.2f}\N{DEGREE SIGN}, {self.observer.lon:.2f}\N{DEGREE SIGN}",
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
        table.set_fontsize(style.font_size)
        table.scale(1, 5)

        # Apply style to all cells
        for row in [0, 1]:
            for col in range(len(values)):
                table[row, col].set_text_props(**style.matplot_kwargs(self.scale))

        # Apply some styles only to the header row
        for col in range(len(values)):
            table[0, col].set_text_props(fontweight="heavy", fontsize=font_size * 1.2)

    def _plot_border(self):
        optic_polygon = self.optic.polygon(self.pos_az, self.pos_alt)

        self.canvas.polygon(
            coordinates=list(zip(*optic_polygon.exterior.coords.xy)),
            style=PolygonStyle(
                fill_color=None,
                edge_color=self.style.border_bg_color.as_hex(),
                edge_width=40,
            ),
        )
