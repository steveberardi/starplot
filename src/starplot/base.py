from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Union
import logging

import numpy as np
import rtree
from adjustText import adjust_text as _adjust_text
from matplotlib import patches
from matplotlib import pyplot as plt, patheffects, transforms
from matplotlib.lines import Line2D
from pytz import timezone
from skyfield.api import Angle

from starplot import geod
from starplot.data import load, ecliptic
from starplot.data.planets import Planet, get_planet_positions, PLANET_LABELS_DEFAULT
from starplot.styles import (
    PlotStyle,
    MarkerStyle,
    ObjectStyle,
    LabelStyle,
    LegendLocationEnum,
    LegendStyle,
    PathStyle,
    PolygonStyle,
)
from starplot.styles.helpers import use_style

LOGGER = logging.getLogger("starplot")
LOG_HANDLER = logging.StreamHandler()
LOG_FORMATTER = logging.Formatter(
    "\033[1;34m%(name)s\033[0m:[%(levelname)s]: %(message)s"
)
LOG_HANDLER.setFormatter(LOG_FORMATTER)
LOGGER.addHandler(LOG_HANDLER)


DEFAULT_FOV_STYLE = PolygonStyle(
    fill=False, edge_color="red", line_style="dashed", edge_width=4, zorder=1000
)
"""Default style for plotting scope and bino field of view circles"""

DEFAULT_STYLE = PlotStyle()


class BasePlot(ABC):
    _background_clip_path = None

    def __init__(
        self,
        dt: datetime = None,
        ephemeris: str = "de421_2001.bsp",
        style: PlotStyle = DEFAULT_STYLE,
        resolution: int = 2048,
        hide_colliding_labels: bool = True,
        *args,
        **kwargs,
    ):
        px = 1 / plt.rcParams["figure.dpi"]  # pixel in inches

        self.pixels_per_point = plt.rcParams["figure.dpi"] / 72

        self.style = style
        self.figure_size = resolution * px
        self.resolution = resolution
        self.hide_colliding_labels = hide_colliding_labels

        self.dt = dt or timezone("UTC").localize(datetime.now())
        self.ephemeris = load(ephemeris)

        self.labels = []
        self._labels_rtree = rtree.index.Index()

        self._legend = None
        self._legend_handles = {}

        self.log_level = logging.DEBUG if kwargs.get("debug") else logging.ERROR
        self.logger = LOGGER
        self.logger.setLevel(self.log_level)

        self.text_border = patheffects.withStroke(
            linewidth=self.style.text_border_width,
            foreground=self.style.background_color.as_hex(),
        )
        self._size_multiplier = self.resolution / 3000
        self.timescale = load.timescale().from_datetime(self.dt)

    def _plot_kwargs(self) -> dict:
        return {}

    def _prepare_coords(self, ra, dec) -> (float, float):
        return ra, dec

    def _is_label_collision(self, extent) -> bool:
        ix = list(
            self._labels_rtree.intersection(
                (extent.x0, extent.y0, extent.x1, extent.y1)
            )
        )
        return len(ix) > 0

    def _maybe_remove_label(self, label) -> None:
        extent = label.get_window_extent(renderer=self.fig.canvas.get_renderer())
        ax_extent = self.ax.get_window_extent()
        intersection = transforms.Bbox.intersection(ax_extent, extent)

        if (
            intersection is not None
            and (
                intersection.height * intersection.width == extent.height * extent.width
            )
            and not (self.hide_colliding_labels and self._is_label_collision(extent))
        ):
            self.labels.append(label)
            self._labels_rtree.insert(0, (extent.x0, extent.y0, extent.x1, extent.y1))
        else:
            label.remove()

    def _add_legend_handle_marker(self, label: str, style: MarkerStyle):
        if label is not None and label not in self._legend_handles:
            s = style.matplot_kwargs()
            s["markersize"] = self.style.legend.symbol_size * self._size_multiplier
            self._legend_handles[label] = Line2D(
                [],
                [],
                **s,
                **self._plot_kwargs(),
                linestyle="None",
                label=label,
            )

    def _plot_text(self, ra: float, dec: float, text: str, *args, **kwargs) -> None:
        x, y = self._prepare_coords(ra, dec)
        kwargs["path_effects"] = kwargs.get("path_effects") or [self.text_border]
        label = self.ax.text(
            x,
            y,
            text,
            *args,
            **kwargs,
            **self._plot_kwargs(),
        )
        label.set_clip_on(True)

        if kwargs.get("clip_path"):
            label.set_clip_path(kwargs.get("clip_path"))

        self._maybe_remove_label(label)

    @use_style(LabelStyle, "title")
    def title(self, text: str, style: LabelStyle = None):
        """
        Plots a title at the top of the plot

        Args:
            text: Title text to plot
            style: Styling of the title. If None, then the plot's style (specified when creating the plot) will be used
        """
        style_kwargs = style.matplot_kwargs(self._size_multiplier)
        style_kwargs.pop("line_spacing", None)
        style_kwargs["pad"] = style.line_spacing
        self.ax.set_title(text, **style_kwargs)

    @use_style(LegendStyle, "legend")
    def legend(self, style: LegendStyle = None):
        """
        Plots the legend.

        If the legend is already plotted, then it'll be removed first and then plotted again. So, it's safe to call this function multiple times if you need to 'refresh' the legend.

        Args:
            style: Styling of the legend. If None, then the plot's style (specified when creating the plot) will be used
        """
        if not self._legend_handles:
            return

        if self._legend is not None:
            self._legend.remove()

        bbox_kwargs = {}

        if style.location == LegendLocationEnum.OUTSIDE_BOTTOM:
            # to plot legends outside the map area, you have to target the figure
            target = self.fig
            bbox_kwargs = dict(
                bbox_to_anchor=(0.5, 0.13), bbox_transform=self.fig.transFigure
            )

        elif style.location == LegendLocationEnum.OUTSIDE_TOP:
            target = self.fig
            bbox_kwargs = dict(
                bbox_to_anchor=(0.5, 0.87), bbox_transform=self.fig.transFigure
            )
        else:
            target = self.ax

        self._legend = target.legend(
            handles=self._legend_handles.values(),
            **style.matplot_kwargs(size_multiplier=self._size_multiplier),
            **bbox_kwargs,
        ).set_zorder(
            # zorder is not a valid kwarg to legend(), so we have to set it afterwards
            style.zorder
        )

    def adjust_text(self, ensure_inside_axes: bool = False, **kwargs) -> None:
        """Adjust all the labels to avoid overlapping. This function uses the [adjustText](https://adjusttext.readthedocs.io/) library.

        Args:
            ensure_inside_axes: If True, then labels will be forced to stay within the axes
            **kwargs: Any keyword arguments to pass through to [adjustText](https://adjusttext.readthedocs.io/en/latest/#adjustText.adjust_text)

        """
        _adjust_text(
            self.labels, ax=self.ax, ensure_inside_axes=ensure_inside_axes, **kwargs
        )

    def close_fig(self) -> None:
        """Closes the underlying matplotlib figure."""
        if self.fig:
            plt.close(self.fig)

    def export(self, filename: str, format: str = "png", padding: float = 0, **kwargs):
        """Exports the plot to an image file.

        Args:
            filename: Filename of exported file
            format: Format of file: "png" or "svg"
            padding: Padding (in inches) around the image
            **kwargs: Any keyword arguments to pass through to matplotlib's `savefig` method

        """
        self.fig.savefig(
            filename,
            format=format,
            bbox_inches="tight",
            pad_inches=padding,
            dpi=144,  # (self.resolution / self.figure_size * 1.28),
            **kwargs,
        )

    @use_style(ObjectStyle)
    def marker(
        self,
        ra: float,
        dec: float,
        label: str,
        style: Union[dict, ObjectStyle],
        legend_label: str = None,
    ) -> None:
        """Plots a marker

        Args:
            ra: Right ascension of the marker
            dec: Declination of the marker
            label: Label for the marker
            style: Styling for the marker
            legend_label: How to label the marker in the legend. If `None`, then the marker will not be added to the legend

        """
        x, y = self._prepare_coords(ra, dec)

        if self.in_bounds(ra, dec):
            self.ax.plot(
                x,
                y,
                **style.marker.matplot_kwargs(size_multiplier=self._size_multiplier),
                **self._plot_kwargs(),
                linestyle="None",
            )

            if legend_label is not None:
                self._add_legend_handle_marker(legend_label, style.marker)

            if label:
                plotted_label = self.ax.text(
                    x,
                    y,
                    label,
                    **style.label.matplot_kwargs(size_multiplier=self._size_multiplier),
                    **self._plot_kwargs(),
                    path_effects=[self.text_border],
                    va="bottom",
                    ha="left",
                )
                plotted_label.set_clip_on(True)
                self._maybe_remove_label(plotted_label)

    @use_style(ObjectStyle, "planets")
    def planets(
        self,
        style: ObjectStyle = None,
        true_size: bool = False,
        labels: Dict[Planet, str] = PLANET_LABELS_DEFAULT,
        legend_label: str = "Planet",
    ) -> None:
        """Plots the planets

        Args:
            style: Styling of the planets. If None, then the plot's style (specified when creating the plot) will be used
            true_size: If True, then each planet's true apparent size in the sky will be plotted. If False, then the style's marker size will be used.
            labels: How the planets will be labeled on the plot and legend. If not specified, then the planet's name will be used (see [`Planet`][starplot.data.planets.Planet])
            legend_label: How to label the planets in the legend. If `None`, then the planets will not be added to the legend
        """
        labels = labels or {}
        planets = get_planet_positions(self.timescale, ephemeris=self.ephemeris)

        for p, planet_data in planets.items():
            ra, dec, apparent_size_degrees = planet_data
            label = labels.get(p)

            if true_size:
                self.plot_circle(
                    (ra, dec),
                    apparent_size_degrees,
                    style.marker.to_polygon_style(),
                )
                self._add_legend_handle_marker(legend_label, style.marker)

                if label:
                    self._plot_text(
                        ra,
                        dec,
                        label.upper(),
                        **style.label.matplot_kwargs(
                            size_multiplier=self._size_multiplier
                        ),
                    )
            else:
                self.marker(
                    ra=ra,
                    dec=dec,
                    label=label.upper() if label else None,
                    style=style,
                    legend_label=legend_label,
                )

    @use_style(ObjectStyle, "moon")
    def moon(
        self,
        style: ObjectStyle = None,
        true_size: bool = False,
        label: str = "Moon",
        legend_label: str = "Moon",
    ) -> None:
        """Plots the Moon

        Args:
            style: Styling of the Moon. If None, then the plot's style (specified when creating the plot) will be used
            true_size: If True, then the Moon's true apparent size in the sky will be plotted. If False, then the style's marker size will be used.
            label: How the Moon will be labeled on the plot and legend
        """
        earth, moon = self.ephemeris["earth"], self.ephemeris["moon"]
        astrometric = earth.at(self.timescale).observe(moon)
        ra, dec, distance = astrometric.radec()

        ra = ra.hours
        dec = dec.degrees

        if not self.in_bounds(ra, dec):
            return

        if true_size:
            radius_km = 1_740
            apparent_diameter_degrees = Angle(
                radians=np.arcsin(radius_km / distance.km) * 2.0
            ).degrees

            self.plot_circle(
                (ra, dec),
                apparent_diameter_degrees,
                style.marker.to_polygon_style(),
            )

            self._add_legend_handle_marker(legend_label, style.marker)

            if label:
                self._plot_text(
                    ra,
                    dec,
                    label,
                    **style.label.matplot_kwargs(size_multiplier=self._size_multiplier),
                )

        else:
            self.marker(
                ra=ra,
                dec=dec,
                label=label,
                style=style,
                legend_label=legend_label,
            )

    @abstractmethod
    def in_bounds(self, ra: float, dec: float) -> bool:
        """Determine if a coordinate is within the bounds of the plot.

        Args:
            ra: Right ascension
            dec: Declination

        Returns:
            bool: True if the coordinate is in bounds, otherwise False

        """
        raise NotImplementedError

    def _polygon(self, points: list, style: PolygonStyle, **kwargs):
        points = [geod.to_radec(p) for p in points]
        points = [self._prepare_coords(*p) for p in points]
        patch = patches.Polygon(
            points,
            # closed=False, # needs to be false for circles at poles?
            **style.matplot_kwargs(size_multiplier=self._size_multiplier),
            **kwargs,
        )
        self.ax.add_patch(patch)

    @use_style(PolygonStyle)
    def polygon(self, points: list, style: PolygonStyle):
        """Plots a polygon of points

        Args:
            points: List of polygon points `[(ra, dec), ...]`
            style: Style of polygon
        """
        _points = [(ra * 15, dec) for ra, dec in points]
        self._polygon(_points, style)

    @use_style(PolygonStyle)
    def rectangle(
        self,
        center: tuple,
        height_degrees: float,
        width_degrees: float,
        style: PolygonStyle,
        angle: float = 0,
        *args,
        **kwargs,
    ):
        """Plots a rectangle

        Args:
            center: Center of rectangle (ra, dec)
            height_degrees: Height of rectangle (degrees)
            width_degrees: Width of rectangle (degrees)
            angle: Angle of rotation clockwise (degrees)
            style: Style of rectangle
        """
        points = geod.rectangle(
            center,
            height_degrees,
            width_degrees,
            angle,
        )
        self._polygon(points, style)

    @use_style(PolygonStyle)
    def ellipse(
        self,
        center: tuple,
        height_degrees: float,
        width_degrees: float,
        style: PolygonStyle,
        angle: float = 0,
        num_pts: int = 100,
    ):
        """Plots an ellipse

        Args:
            center: Center of ellipse (ra, dec)
            height_degrees: Height of ellipse (degrees)
            width_degrees: Width of ellipse (degrees)
            style: Style of ellipse
            angle: Angle of rotation clockwise (degrees)
            num_pts: Number of points to calculate for the ellipse polygon
        """

        points = geod.ellipse(
            center,
            height_degrees,
            width_degrees,
            angle,
            num_pts,
        )
        self._polygon(points, style)

    @use_style(PolygonStyle)
    def circle(
        self,
        center: tuple,
        radius_degrees: float,
        style: PolygonStyle,
        num_pts: int = 100,
    ):
        """Plots a circle

        Args:
            center: Center of circle (ra, dec)
            radius_degrees: Radius of circle (degrees)
            style: Style of circle
            num_pts: Number of points to calculate for the circle polygon
        """
        self.ellipse(
            center,
            radius_degrees * 2,
            radius_degrees * 2,
            style,
            angle=0,
            num_pts=num_pts,
        )

    def _fov_circle(
        self, ra, dec, fov, magnification, style: PolygonStyle = DEFAULT_FOV_STYLE
    ):
        # FOV (degrees) = FOV eyepiece / magnification
        fov_degrees = fov / magnification
        fov_radius = fov_degrees / 2
        self.circle(
            (ra, dec),
            fov_radius,
            style,
        )

    @use_style(PolygonStyle)
    def scope_fov(
        self,
        ra: float,
        dec: float,
        scope_focal_length: float,
        eyepiece_focal_length: float,
        eyepiece_fov: float,
        style: PolygonStyle = DEFAULT_FOV_STYLE,
    ):
        """Draws a circle representing the field of view for a telescope and eyepiece.

        Args:
            ra: Right ascension of the center of view
            dec: Declination of the center of view
            scope_focal_length: focal length (mm) of the scope
            eyepiece_focal_length: focal length (mm) of the eyepiece
            eyepiece_fov: field of view (degrees) of the eyepiece
            style: style of the polygon
        """
        # FOV (degrees) = FOV eyepiece / magnification
        magnification = scope_focal_length / eyepiece_focal_length
        self._fov_circle(ra, dec, eyepiece_fov, magnification, style)

    @use_style(PolygonStyle)
    def bino_fov(
        self,
        ra: float,
        dec: float,
        fov: float,
        magnification: float,
        style: PolygonStyle = DEFAULT_FOV_STYLE,
    ):
        """Draws a circle representing the field of view for binoculars.

        Args:
            ra: Right ascension of the center of view
            dec: Declination of the center of view
            fov: field of view (degrees) of the binoculars
            magnification: magnification of the binoculars
            style: style of the polygon
        """
        self._fov_circle(ra, dec, fov, magnification, style)

    @use_style(PathStyle, "ecliptic")
    def ecliptic(self, style: PathStyle = None, label: str = "ECLIPTIC"):
        """Plots the ecliptic

        Args:
            style: Styling of the ecliptic. If None, then the plot's style will be used
            label: How the ecliptic will be labeled on the plot
        """
        x = []
        y = []
        inbounds = []

        for ra, dec in ecliptic.RA_DECS:
            x0, y0 = self._prepare_coords(ra, dec)
            x.append(x0)
            y.append(y0)
            if self.in_bounds(ra, dec):
                inbounds.append((ra, dec))

        self.ax.plot(
            x,
            y,
            dash_capstyle=style.line.dash_capstyle,
            clip_path=self._background_clip_path,
            **style.line.matplot_kwargs(self._size_multiplier),
            **self._plot_kwargs(),
        )

        if label:
            if len(inbounds) > 4:
                label_spacing = int(len(inbounds) / 3) or 1

                for i in range(0, len(inbounds), label_spacing):
                    ra, dec = inbounds[i]
                    self._plot_text(
                        ra,
                        dec - 0.4,
                        label,
                        **self.style.ecliptic.label.matplot_kwargs(
                            self._size_multiplier
                        ),
                    )

    @use_style(PathStyle, "celestial_equator")
    def celestial_equator(
        self, style: PathStyle = None, label: str = "CELESTIAL EQUATOR"
    ):
        """
        Plots the celestial equator

        Args:
            style: Styling of the celestial equator. If None, then the plot's style will be used
            label: How the celestial equator will be labeled on the plot
        """
        x = []
        y = []

        # TODO : handle wrapping

        ra_start = max(0, int(self.ra_min) - 2) * 100
        ra_end = min(24, int(self.ra_max) + 2) * 100

        for ra in range(ra_start, ra_end, 2):
            x0, y0 = self._prepare_coords(ra / 100, 0)
            x.append(x0)
            y.append(y0)

        self.ax.plot(
            x,
            y,
            clip_path=self._background_clip_path,
            **style.line.matplot_kwargs(self._size_multiplier),
            **self._plot_kwargs(),
        )

        if label:
            label_style_kwargs = style.label.matplot_kwargs(self._size_multiplier)
            label_spacing = (self.ra_max - self.ra_min) / 3
            for ra in np.arange(self.ra_min, self.ra_max, label_spacing):
                self._plot_text(ra, 0.25, label, **label_style_kwargs)
