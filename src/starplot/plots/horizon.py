import math

from functools import cache
from typing import Callable

import pandas as pd

from skyfield.api import Star as SkyfieldStar
from shapely import Polygon, MultiPolygon

from starplot import geometry
from starplot.coordinates import CoordinateSystem
from starplot.projections import LambertAzEqArea, CoordinateReferenceSystem
from starplot.mixins import ExtentMaskMixin
from starplot.models.observer import Observer

from starplot.styles import (
    PlotStyle,
    extensions,
    use_style,
    PathStyle,
)
from starplot.plots.base import BasePlot
from starplot.plotters.text import CollisionHandler
from starplot.plotters import (
    ConstellationPlotterMixin,
    MilkyWayPlotterMixin,
    ArrowPlotterMixin,
    DsoPlotterMixin,
    TextPlotterMixin,
    LegendPlotterMixin,
)

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
    DsoPlotterMixin,
    MilkyWayPlotterMixin,
    LegendPlotterMixin,
    ArrowPlotterMixin,
    TextPlotterMixin,
):
    """Creates a new horizon plot.

    Args:
        altitude: Tuple of altitude range to plot (min, max)
        azimuth: Tuple of azimuth range to plot (min, max)
        observer: Observer instance which specifies a time and place. Defaults to `Observer()`
        ephemeris: Ephemeris to use for calculating planet positions (see [Skyfield's documentation](https://rhodesmill.org/skyfield/planets.html) for details)
        style: Styling for the plot (colors, sizes, fonts, etc). If `None`, it defaults to `PlotStyle()`
        resolution: Size (in pixels) of largest dimension of the map
        point_label_handler: Default [CollisionHandler][starplot.CollisionHandler] for point labels.
        area_label_handler: Default [CollisionHandler][starplot.CollisionHandler] for area labels.
        path_label_handler: Default [CollisionHandler][starplot.CollisionHandler] for path labels.
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
        altitude: tuple[float, float],
        azimuth: tuple[float, float],
        observer: Observer = None,
        ephemeris: str = "de421.bsp",
        style: PlotStyle = None,
        resolution: int = 4096,
        point_label_handler: CollisionHandler = None,
        area_label_handler: CollisionHandler = None,
        path_label_handler: CollisionHandler = None,
        scale: float = 1.0,
        autoscale: bool = False,
        suppress_warnings: bool = True,
        *args,
        **kwargs,
    ) -> "HorizonPlot":
        observer = observer or Observer()
        style = style or PlotStyle().extend(extensions.MAP)

        if azimuth[0] >= azimuth[1]:
            raise ValueError("Azimuth min must be less than max")
        if azimuth[1] - azimuth[0] > 180:
            raise ValueError("Azimuth range cannot be greater than 180 degrees")

        if altitude[0] >= altitude[1]:
            raise ValueError("Altitude min must be less than max")
        if altitude[1] - altitude[0] > 90:
            raise ValueError("Altitude range cannot be greater than 90 degrees")

        self.alt = altitude
        self.az = azimuth
        self._alt = altitude
        self._az = azimuth
        self.center_alt = sum(altitude) / 2
        self.center_az = sum(azimuth) / 2

        if self.center_az > 360:
            self.center_az -= 360

        projection = LambertAzEqArea(center_ra=self.center_az, center_dec=0)
        bounds = [azimuth[0], altitude[0], azimuth[1], altitude[1]]

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
            bounds=bounds,
            invert_x=False,
            invert_y=False,
            clip_path=None,
            crs=CoordinateReferenceSystem.ENU,
            *args,
            **kwargs,
        )
        self.logger.debug("Creating HorizonPlot...")

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

    def _prepare_star_coords(self, df, limit_by_altaz=True):
        df["x"], df["y"] = self.observer._apparent(
            obj=SkyfieldStar.from_dataframe(df),
            ephemeris=self.ephemeris_name,
        )

        # if limit_by_altaz:
        #     extent = self._extent_mask_altaz()
        #     df["_geometry_az_alt"] = gpd.points_from_xy(df.x, df.y)
        #     df = df[df["_geometry_az_alt"].intersects(extent)]

        return df

    def _calc_position(self):
        self.observe = self.observer.observe(self.ephemeris_name)

        self.ra_min = 0
        self.ra_max = 360
        self.dec_min = self.observer.lat - 90
        self.dec_max = self.observer.lat + 90

        self.logger.debug(
            f"Extent = RA ({self.ra_min:.2f}, {self.ra_max:.2f}) DEC ({self.dec_min:.2f}, {self.dec_max:.2f})"
        )

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
        ax, ay = self.canvas._to_axes(az, alt)
        return 0 <= ax <= 1 and 0 <= ay <= 1

    def _in_bounds_xy(self, x: float, y: float) -> bool:
        return self.in_bounds_altaz(y, x)  # alt = y, az = x

    @cache
    def _extent_mask_altaz(self):
        """
        Returns shapely geometry objects of the alt/az extent

        If the extent crosses North cardinal direction, then a MultiPolygon will be returned
        """
        extent = self.canvas.bounds
        alt_min, alt_max = extent[2], extent[3]
        az_min, az_max = extent[0], extent[1]

        # az_ul, _ = self._ax_to_azalt(0, 1)
        # az_ur, _ = self._ax_to_azalt(1, 1)

        # if az_ul < 0:
        #     az_ul += 360

        # if az_ur < 0:
        #     az_ur += 360

        # az_min = min(self.az[0], self.az[1], az_ul, az_ur)
        # az_max = max(self.az[0], self.az[1], az_ul, az_ur)

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
        return

        # TODO
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
        labels: bool = True,
        az_locations: list[float] = None,
        alt_locations: list[float] = None,
        az_formatter_fn: Callable[[float], str] = None,
        alt_formatter_fn: Callable[[float], str] = None,
        show_ticks: bool = True,
        tick_step: int = 5,
    ):
        """
        Plots gridlines

        Args:
            style: Styling of the gridlines. If None, then the plot's style (specified when creating the plot) will be used
            labels: If True, then labels for each gridline will be plotted on the outside of the axes.
            az_locations: List of azimuth locations for the gridlines (in degrees, 0...360). Defaults to every 15 degrees
            alt_locations: List of altitude locations for the gridlines (in degrees, -90...90). Defaults to every 10 degrees.
            az_formatter_fn: Callable for creating labels of azimuth gridlines
            alt_formatter_fn: Callable for creating labels of altitude gridlines
            show_ticks: If True, then tick marks will be plotted on the horizon path for every `tick_step` degree that is not also a degree label
            tick_step: Step size for tick marks
        """
        _labels = []

        def az_formatter_fn_default(az):
            cardinal_directions = {
                0: "NORTH",
                90: "EAST",
                180: "SOUTH",
                270: "WEST",
            }
            return cardinal_directions.get(az) or f"{round(az)}\u00b0"

        alt_formatter_fn_default = lambda alt: f"{round(alt)}\u00b0"  # noqa: E731

        az_formatter_fn = az_formatter_fn or az_formatter_fn_default
        alt_formatter_fn = alt_formatter_fn or alt_formatter_fn_default

        x_locations = az_locations or [x for x in range(0, 360, 15)]
        y_locations = alt_locations or [y for y in range(-80, 90, 10)]

        for x in x_locations:
            coords = geometry.line_segment((x, -20), (x, 90), 0.5)
            self.canvas.line(
                coordinates=coords,
                style=style.line,
            )
            if labels:
                _labels.append((coords, az_formatter_fn(x), ("bottom",)))

        for y in y_locations:
            coords = geometry.line_segment((0.00001, y), (359.99999, y), 0.5)
            self.canvas.line(
                coordinates=coords,
                style=style.line,
            )

            if labels:
                _labels.append((coords, alt_formatter_fn(y), ("left", "right")))

        if not labels:
            return

        self.canvas._clip_path_border(self.style.horizon, labels=_labels)

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
