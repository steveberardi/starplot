from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Union, Optional
from random import randrange
import logging

import numpy as np
import rtree
from matplotlib import patches
from matplotlib import pyplot as plt, patheffects
from matplotlib.lines import Line2D
from pytz import timezone
from shapely import Polygon, Point

from starplot.coordinates import CoordinateSystem
from starplot import geod, models, warnings
from starplot.data import load, ecliptic
from starplot.models.planet import PlanetName, PLANET_LABELS_DEFAULT
from starplot.models.moon import MoonPhase
from starplot.styles import (
    AnchorPointEnum,
    PlotStyle,
    MarkerStyle,
    ObjectStyle,
    LabelStyle,
    LegendLocationEnum,
    LegendStyle,
    LineStyle,
    MarkerSymbolEnum,
    PathStyle,
    PolygonStyle,
    fonts,
)
from starplot.styles.helpers import use_style
from starplot.geometry import (
    unwrap_polygon_360,
    random_point_in_polygon_at_distance,
)
from starplot.profile import profile

LOGGER = logging.getLogger("starplot")
LOG_HANDLER = logging.StreamHandler()
LOG_FORMATTER = logging.Formatter(
    "\033[1;34m%(name)s\033[0m:[%(levelname)s]: %(message)s"
)
LOG_HANDLER.setFormatter(LOG_FORMATTER)
LOGGER.addHandler(LOG_HANDLER)


DEFAULT_FOV_STYLE = PolygonStyle(
    fill_color=None,
    edge_color="red",
    line_style=[1, [2, 3]],
    edge_width=3,
    zorder=-1000,
)
"""Default style for plotting scope and bino field of view circles"""

DEFAULT_STYLE = PlotStyle()

DEFAULT_RESOLUTION = 4096

DPI = 100


class BasePlot(ABC):
    _background_clip_path = None
    _clip_path_polygon: Polygon = None  # clip path in display coordinates
    _coordinate_system = CoordinateSystem.RA_DEC

    def __init__(
        self,
        dt: datetime = None,
        ephemeris: str = "de421_2001.bsp",
        style: PlotStyle = DEFAULT_STYLE,
        resolution: int = 4096,
        hide_colliding_labels: bool = True,
        scale: float = 1.0,
        autoscale: bool = False,
        suppress_warnings: bool = True,
        *args,
        **kwargs,
    ):
        px = 1 / DPI  # plt.rcParams["figure.dpi"]  # pixel in inches
        self.pixels_per_point = DPI / 72

        self.style = style
        self.figure_size = resolution * px
        self.resolution = resolution
        self.hide_colliding_labels = hide_colliding_labels

        self.scale = scale
        self.autoscale = autoscale
        if self.autoscale:
            self.scale = self.resolution / DEFAULT_RESOLUTION

        if suppress_warnings:
            warnings.suppress()

        self.dt = dt or timezone("UTC").localize(datetime.now())
        self._ephemeris_name = ephemeris
        self.ephemeris = load(ephemeris)
        self.earth = self.ephemeris["earth"]

        self.labels = []
        self._labels_rtree = rtree.index.Index()
        self._constellations_rtree = rtree.index.Index()
        self._stars_rtree = rtree.index.Index()
        self._markers_rtree = rtree.index.Index()

        self._background_clip_path = None

        self._legend = None
        self._legend_handles = {}

        self.log_level = logging.DEBUG if kwargs.get("debug") else logging.ERROR
        self.logger = LOGGER
        self.logger.setLevel(self.log_level)

        self.text_border = patheffects.withStroke(
            linewidth=self.style.text_border_width * self.scale,
            foreground=self.style.text_border_color.as_hex(),
        )
        self.timescale = load.timescale().from_datetime(self.dt)

        self._objects = models.ObjectList()
        self._labeled_stars = []
        fonts.load()

    def _plot_kwargs(self) -> dict:
        return {}

    def _prepare_coords(self, ra, dec) -> tuple[float, float]:
        return ra, dec

    def _update_clip_path_polygon(self, buffer=8):
        coords = self._background_clip_path.get_verts()
        self._clip_path_polygon = Polygon(coords).buffer(-1 * buffer)

    def _is_label_collision(self, bbox) -> bool:
        ix = list(self._labels_rtree.intersection(bbox))
        return len(ix) > 0

    def _is_constellation_collision(self, bbox) -> bool:
        ix = list(self._constellations_rtree.intersection(bbox))
        return len(ix) > 0

    def _is_star_collision(self, bbox) -> bool:
        ix = list(self._stars_rtree.intersection(bbox))
        return len(ix) > 0

    def _is_marker_collision(self, bbox) -> bool:
        ix = list(self._markers_rtree.intersection(bbox))
        return len(ix) > 0

    def _is_clipped(self, points) -> bool:
        p = self._clip_path_polygon

        for x, y in points:
            if not p.contains(Point(x, y)):
                return True

        return False

    def _add_label_to_rtree(self, label, extent=None):
        extent = extent or label.get_window_extent(
            renderer=self.fig.canvas.get_renderer()
        )
        self.labels.append(label)
        self._labels_rtree.insert(
            0, np.array((extent.x0 - 1, extent.y0 - 1, extent.x1 + 1, extent.y1 + 1))
        )

    def _is_open_space(
        self,
        bbox: tuple[float, float, float, float],
        padding=0,
        avoid_clipped=True,
        avoid_label_collisions=True,
        avoid_marker_collisions=True,
        avoid_constellation_collision=True,
    ) -> bool:
        """
        Returns true if the boox covers an open space (i.e. no collisions)

        Args:
            bbox: 4-element tuple of lower left and upper right coordinates
        """
        x0, y0, x1, y1 = bbox
        points = [(x0, y0), (x1, y1)]
        bbox = (
            x0 - padding,
            y0 - padding,
            x1 + padding,
            y1 + padding,
        )

        if any([np.isnan(c) for c in (x0, y0, x1, y1)]):
            return False

        if avoid_clipped and self._is_clipped(points):
            return False

        if avoid_label_collisions and self._is_label_collision(bbox):
            return False

        if avoid_marker_collisions and (
            self._is_star_collision(bbox) or self._is_marker_collision(bbox)
        ):
            return False

        if avoid_constellation_collision and self._is_constellation_collision(bbox):
            return False

        return True

    def _get_label_bbox(self, label):
        extent = label.get_window_extent(renderer=self.fig.canvas.get_renderer())
        return (extent.x0, extent.y0, extent.x1, extent.y1)

    def _maybe_remove_label(
        self,
        label,
        remove_on_collision=True,
        remove_on_clipped=True,
        remove_on_constellation_collision=True,
        padding=0,
    ) -> bool:
        """Returns true if the label is removed, else false"""
        extent = label.get_window_extent(renderer=self.fig.canvas.get_renderer())
        bbox = (
            extent.x0 - padding,
            extent.y0 - padding,
            extent.x1 + padding,
            extent.y1 + padding,
        )
        points = [(extent.x0, extent.y0), (extent.x1, extent.y1)]

        if any([np.isnan(c) for c in (extent.x0, extent.y0, extent.x1, extent.y1)]):
            label.remove()
            return True

        if remove_on_clipped and self._is_clipped(points):
            label.remove()
            return True

        if remove_on_collision and (
            self._is_label_collision(bbox)
            or self._is_star_collision(bbox)
            or self._is_marker_collision(bbox)
        ):
            label.remove()
            return True

        if remove_on_constellation_collision and self._is_constellation_collision(bbox):
            label.remove()
            return True

        return False

    def _add_legend_handle_marker(self, label: str, style: MarkerStyle):
        if label is not None and label not in self._legend_handles:
            s = style.matplot_kwargs()
            s["markersize"] = self.style.legend.symbol_size * self.scale
            self._legend_handles[label] = Line2D(
                [],
                [],
                **s,
                **self._plot_kwargs(),
                linestyle="None",
                label=label,
            )

    def _collision_score(self, label) -> int:
        config = {
            "labels": 1.0,  # always fail
            "stars": 0.5,
            "constellations": 0.8,
            "anchors": [
                ("bottom right", 0),
                ("top right", 0.2),
                ("top left", 0.5),
            ],
            "on_fail": "plot",
        }
        extent = label.get_window_extent(renderer=self.fig.canvas.get_renderer())

        if any(
            [np.isnan(c) for c in (extent.x0, extent.y0, extent.x1, extent.y1)]
        ) or self._is_clipped(extent):
            return 1

        x_labels = (
            len(
                list(
                    self._labels_rtree.intersection(
                        (extent.x0, extent.y0, extent.x1, extent.y1)
                    )
                )
            )
            * config["labels"]
        )

        if x_labels >= 1:
            return 1

        x_constellations = (
            len(
                list(
                    self._constellations_rtree.intersection(
                        (extent.x0, extent.y0, extent.x1, extent.y1)
                    )
                )
            )
            * config["constellations"]
        )

        if x_constellations >= 1:
            return 1

        x_stars = (
            len(
                list(
                    self._stars_rtree.intersection(
                        (extent.x0, extent.y0, extent.x1, extent.y1)
                    )
                )
            )
            * config["stars"]
        )
        if x_stars >= 1:
            return 1

        return sum([x_labels, x_constellations, x_stars]) / 3

    def _text(self, x, y, text, **kwargs):
        label = self.ax.annotate(
            text,
            (x, y),
            **kwargs,
            **self._plot_kwargs(),
        )
        if kwargs.get("clip_on"):
            label.set_clip_on(True)
            label.set_clip_path(self._background_clip_path)
        return label

    def _text_point(
        self,
        ra: float,
        dec: float,
        text: str,
        hide_on_collision: bool = True,
        force: bool = False,
        clip_on: bool = True,
        **kwargs,
    ):
        if not text:
            return None

        x, y = self._prepare_coords(ra, dec)
        kwargs["path_effects"] = kwargs.get("path_effects", [self.text_border])
        remove_on_constellation_collision = kwargs.pop(
            "remove_on_constellation_collision", True
        )

        original_va = kwargs.pop("va", None)
        original_ha = kwargs.pop("ha", None)
        original_offset_x, original_offset_y = kwargs.pop("xytext", (0, 0))

        anchors = [(original_va, original_ha)]
        for a in self.style.text_anchor_fallbacks:
            d = AnchorPointEnum.from_str(a).as_matplot()
            anchors.append((d["va"], d["ha"]))

        for va, ha in anchors:
            offset_x, offset_y = original_offset_x, original_offset_y
            if original_ha != ha:
                offset_x *= -1

            if original_va != va:
                offset_y *= -1

            if ha == "center":
                offset_x = 0
                offset_y = 0

            label = self._text(
                x, y, text, **kwargs, va=va, ha=ha, xytext=(offset_x, offset_y)
            )
            removed = self._maybe_remove_label(
                label,
                remove_on_collision=hide_on_collision,
                remove_on_clipped=clip_on,
                remove_on_constellation_collision=remove_on_constellation_collision,
            )

            if force or not removed:
                self._add_label_to_rtree(label)
                return label

    def _text_area(
        self,
        ra: float,
        dec: float,
        text: str,
        area,
        hide_on_collision: bool = True,
        force: bool = False,
        clip_on: bool = True,
        settings: dict = None,
        **kwargs,
    ) -> None:
        kwargs["path_effects"] = kwargs.get("path_effects", [self.text_border])
        kwargs["va"] = "center"
        kwargs["ha"] = "center"

        avoid_constellation_lines = settings.get("avoid_constellation_lines", False)
        padding = settings.get("label_padding", 3)
        settings.get("buffer", 0.1)
        max_distance = settings.get("max_distance", 300)
        distance_step_size = settings.get("distance_step_size", 1)
        point_iterations = settings.get("point_generation_max_iterations", 500)
        random_seed = settings.get("seed")

        attempts = 0
        height = None
        width = None
        bbox = None
        areas = (
            [p for p in area.geoms] if "MultiPolygon" == str(area.geom_type) else [area]
        )
        new_areas = []
        origin = Point(ra, dec)

        for a in areas:
            unwrapped = unwrap_polygon_360(a)
            # new_buffer = unwrapped.area / 10 * -1 * buffer * self.scale
            # new_buffer = -1 * buffer * self.scale
            # new_poly = unwrapped.buffer(new_buffer)
            new_areas.append(unwrapped)

        for d in range(0, max_distance, distance_step_size):
            distance = d / 20
            poly = randrange(len(new_areas))
            point = random_point_in_polygon_at_distance(
                new_areas[poly],
                origin_point=origin,
                distance=distance,
                max_iterations=point_iterations,
                seed=random_seed,
            )

            if point is None:
                continue

            x, y = self._prepare_coords(point.x, point.y)

            if height and width:
                data_xy = self._proj.transform_point(x, y, self._crs)
                display_x, display_y = self.ax.transData.transform(data_xy)
                bbox = (
                    display_x - width / 2,
                    display_y - height / 2,
                    display_x + width / 2,
                    display_y + height / 2,
                )
                label = None

            else:
                label = self._text(x, y, text, **kwargs)
                bbox = self._get_label_bbox(label)
                height = bbox[3] - bbox[1]
                width = bbox[2] - bbox[0]

            is_open = self._is_open_space(
                bbox,
                padding=padding,
                avoid_clipped=clip_on,
                avoid_constellation_collision=avoid_constellation_lines,
                avoid_marker_collisions=hide_on_collision,
                avoid_label_collisions=hide_on_collision,
            )

            # # TODO : remove label if not fully inside area?

            attempts += 1

            if is_open and label is None:
                label = self._text(x, y, text, **kwargs)

            if is_open:
                self._add_label_to_rtree(label)
                return label
            elif label is not None:
                label.remove()

    @use_style(LabelStyle)
    def text(
        self,
        text: str,
        ra: float,
        dec: float,
        style: LabelStyle = None,
        hide_on_collision: bool = True,
        **kwargs,
    ):
        """
        Plots text

        Args:
            text: Text to plot
            ra: Right ascension of text (0...24)
            dec: Declination of text (-90...90)
            style: Styling of the text
            hide_on_collision: If True, then the text will not be plotted if it collides with another label
        """
        if not text:
            return

        style = style or LabelStyle()

        if style.offset_x == "auto":
            style.offset_x = 0

        if style.offset_y == "auto":
            style.offset_y = 0

        if kwargs.get("area"):
            return self._text_area(
                ra,
                dec,
                text,
                **style.matplot_kwargs(self.scale),
                area=kwargs.pop("area"),
                hide_on_collision=hide_on_collision,
                xycoords="data",
                xytext=(style.offset_x * self.scale, style.offset_y * self.scale),
                textcoords="offset points",
                settings=kwargs.pop("auto_adjust_settings"),
                **kwargs,
            )
        else:
            return self._text_point(
                ra,
                dec,
                text,
                **style.matplot_kwargs(self.scale),
                hide_on_collision=hide_on_collision,
                xycoords="data",
                xytext=(style.offset_x * self.scale, style.offset_y * self.scale),
                textcoords="offset points",
                **kwargs,
            )

    @property
    def objects(self) -> models.ObjectList:
        """
        Returns an [`ObjectList`][starplot.models.ObjectList] that contains various lists of sky objects that have been plotted.
        """
        return self._objects

    @use_style(LabelStyle, "title")
    def title(self, text: str, style: LabelStyle = None):
        """
        Plots a title at the top of the plot

        Args:
            text: Title text to plot
            style: Styling of the title. If None, then the plot's style (specified when creating the plot) will be used
        """
        style_kwargs = style.matplot_kwargs(self.scale)
        style_kwargs.pop("linespacing", None)
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
        if self._legend is not None:
            self._legend.remove()

        if not self._legend_handles:
            return

        bbox_kwargs = {}

        if style.location == LegendLocationEnum.OUTSIDE_BOTTOM:
            style.location = "lower center"
            offset_y = -0.08
            if getattr(self, "_axis_labels", False):
                offset_y -= 0.05
            bbox_kwargs = dict(
                bbox_to_anchor=(0.5, offset_y),
            )

        elif style.location == LegendLocationEnum.OUTSIDE_TOP:
            style.location = "upper center"
            offset_y = 1.08
            if getattr(self, "_axis_labels", False):
                offset_y += 0.05
            bbox_kwargs = dict(
                bbox_to_anchor=(0.5, offset_y),
            )

        self._legend = self.ax.legend(
            handles=self._legend_handles.values(),
            **style.matplot_kwargs(self.scale),
            **bbox_kwargs,
        ).set_zorder(
            # zorder is not a valid kwarg to legend(), so we have to set it afterwards
            style.zorder
        )

    def close_fig(self) -> None:
        """Closes the underlying matplotlib figure."""
        if self.fig:
            plt.close(self.fig)

    @profile
    def export(self, filename: str, format: str = "png", padding: float = 0, **kwargs):
        """Exports the plot to an image file.

        Args:
            filename: Filename of exported file
            format: Format of file (options are "png", "jpeg", or "svg")
            padding: Padding (in inches) around the image
            **kwargs: Any keyword arguments to pass through to matplotlib's `savefig` method

        """
        self.logger.debug("Exporting...")
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
        style: Union[dict, ObjectStyle],
        label: Optional[str] = None,
        legend_label: str = None,
        skip_bounds_check: bool = False,
        **kwargs,
    ) -> None:
        """Plots a marker

        Args:
            ra: Right ascension of the marker
            dec: Declination of the marker
            label: Label for the marker
            style: Styling for the marker
            legend_label: How to label the marker in the legend. If `None`, then the marker will not be added to the legend
            skip_bounds_check: If True, then don't check the marker coordinates to ensure they're within the bounds of the plot. If you're plotting many markers, setting this to True can speed up plotting time.

        """

        if not skip_bounds_check and not self.in_bounds(ra, dec):
            return

        # Plot marker
        x, y = self._prepare_coords(ra, dec)
        style_kwargs = style.marker.matplot_scatter_kwargs(self.scale)
        self.ax.scatter(
            x,
            y,
            **style_kwargs,
            **self._plot_kwargs(),
            clip_on=True,
            clip_path=self._background_clip_path,
            gid=kwargs.get("gid_marker") or "marker",
        )

        # Add to spatial index
        data_xy = self._proj.transform_point(x, y, self._crs)
        display_x, display_y = self.ax.transData.transform(data_xy)
        if display_x > 0 and display_y > 0:
            radius = style_kwargs.get("s", 1) ** 0.5 / 5
            bbox = np.array(
                (
                    display_x - radius,
                    display_y - radius,
                    display_x + radius,
                    display_y + radius,
                )
            )
            self._markers_rtree.insert(0, bbox, None)

        # Plot label
        if label:
            label_style = style.label
            if label_style.offset_x == "auto" or label_style.offset_y == "auto":
                marker_size = ((style.marker.size / self.scale) ** 2) * (
                    self.scale**2
                )

                label_style = label_style.offset_from_marker(
                    marker_symbol=style.marker.symbol,
                    marker_size=marker_size,
                    scale=self.scale,
                )
            self.text(
                label,
                ra,
                dec,
                label_style,
                hide_on_collision=self.hide_colliding_labels,
                gid=kwargs.get("gid_label") or "marker-label",
            )

        if legend_label is not None:
            self._add_legend_handle_marker(legend_label, style.marker)

    @use_style(ObjectStyle, "planets")
    def planets(
        self,
        style: ObjectStyle = None,
        true_size: bool = False,
        labels: Dict[PlanetName, str] = PLANET_LABELS_DEFAULT,
        legend_label: str = "Planet",
    ) -> None:
        """
        Plots the planets.

        If you specified a lat/lon when creating the plot (e.g. for perspective projections or optic plots), then the planet's _apparent_ RA/DEC will be calculated.

        Args:
            style: Styling of the planets. If None, then the plot's style (specified when creating the plot) will be used
            true_size: If True, then each planet's true apparent size in the sky will be plotted. If False, then the style's marker size will be used.
            labels: How the planets will be labeled on the plot and legend. If not specified, then the planet's name will be used (see [`Planet`][starplot.models.planet.PlanetName])
            legend_label: How to label the planets in the legend. If `None`, then the planets will not be added to the legend
        """
        labels = labels or {}
        planets = models.Planet.all(self.dt, self.lat, self.lon, self._ephemeris_name)

        for p in planets:
            label = labels.get(p.name)

            if self.in_bounds(p.ra, p.dec):
                self._objects.planets.append(p)

            if true_size:
                polygon_style = style.marker.to_polygon_style()
                polygon_style.edge_color = None
                self.circle(
                    (p.ra, p.dec),
                    p.apparent_size,
                    polygon_style,
                    gid="planet-marker",
                )
                self._add_legend_handle_marker(legend_label, style.marker)

                if label:
                    self.text(
                        label.upper(), p.ra, p.dec, style.label, gid="planet-label"
                    )
            else:
                self.marker(
                    ra=p.ra,
                    dec=p.dec,
                    style=style,
                    label=label.upper() if label else None,
                    legend_label=legend_label,
                    gid_marker="planet-marker",
                    gid_label="planet-label",
                )

    @use_style(ObjectStyle, "sun")
    def sun(
        self,
        style: ObjectStyle = None,
        true_size: bool = False,
        label: str = "Sun",
        legend_label: str = "Sun",
    ) -> None:
        """
        Plots the Sun.

        If you specified a lat/lon when creating the plot (e.g. for perspective projections or optic plots), then the Sun's _apparent_ RA/DEC will be calculated.

        Args:
            style: Styling of the Sun. If None, then the plot's style (specified when creating the plot) will be used
            true_size: If True, then the Sun's true apparent size in the sky will be plotted as a circle (the marker style's symbol will be ignored). If False, then the style's marker size will be used.
            label: How the Sun will be labeled on the plot
            legend_label: How the sun will be labeled in the legend
        """
        s = models.Sun.get(
            dt=self.dt, lat=self.lat, lon=self.lon, ephemeris=self._ephemeris_name
        )
        s.name = label or s.name

        if not self.in_bounds(s.ra, s.dec):
            return

        self._objects.sun = s

        if true_size:
            polygon_style = style.marker.to_polygon_style()

            # hide the edge because it can interfere with the true size
            polygon_style.edge_color = None

            self.circle(
                (s.ra, s.dec),
                s.apparent_size,
                style=polygon_style,
                gid="sun-marker",
            )

            style.marker.symbol = MarkerSymbolEnum.CIRCLE
            self._add_legend_handle_marker(legend_label, style.marker)

            if label:
                self.text(label, s.ra, s.dec, style.label, gid="sun-label")

        else:
            self.marker(
                ra=s.ra,
                dec=s.dec,
                style=style,
                label=label,
                legend_label=legend_label,
                gid_marker="sun-marker",
                gid_label="sun-label",
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

    @abstractmethod
    def _in_bounds_xy(self, x: float, y: float) -> bool:
        """
        Determine if a data / projected coordinate is within the non-clipped bounds of the plot.

        This should be extremely precise.

        Args:
            x: X coordinate
            y: Y coordinate

        Returns:
            bool: True if the coordinate is in bounds, otherwise False
        """
        raise NotImplementedError

    def _polygon(self, points: list, style: PolygonStyle, **kwargs):
        points = [self._prepare_coords(*p) for p in points]
        patch = patches.Polygon(
            points,
            # closed=False, # needs to be false for circles at poles?
            **style.matplot_kwargs(self.scale),
            **kwargs,
            # clip_on=True,
            # clip_path=self._background_clip_path,
        )
        self.ax.add_patch(patch)
        # Need to set clip path AFTER adding patch
        patch.set_clip_on(True)
        patch.set_clip_path(self._background_clip_path)

    @use_style(PolygonStyle)
    def polygon(
        self,
        style: PolygonStyle,
        points: list = None,
        geometry: Polygon = None,
        legend_label: str = None,
        **kwargs,
    ):
        """
        Plots a polygon.

        Must pass in either `points` **or** `geometry` (but not both).

        Args:
            style: Style of polygon
            points: List of polygon points `[(ra, dec), ...]` - **must be in counterclockwise order**
            geometry: A shapely Polygon. If this value is passed, then the `points` kwarg will be ignored.
            legend_label: Label for this object in the legend

        """
        if points is None and geometry is None:
            raise ValueError("Must pass points or geometry when plotting polygons.")

        if geometry is not None:
            points = list(zip(*geometry.exterior.coords.xy))

        self._polygon(points, style, gid=kwargs.get("gid") or "polygon")

        if legend_label is not None:
            self._add_legend_handle_marker(
                legend_label,
                style=style.to_marker_style(symbol=MarkerSymbolEnum.SQUARE),
            )

    @use_style(PolygonStyle)
    def rectangle(
        self,
        center: tuple,
        height_degrees: float,
        width_degrees: float,
        style: PolygonStyle,
        angle: float = 0,
        legend_label: str = None,
        **kwargs,
    ):
        """Plots a rectangle

        Args:
            center: Center of rectangle (ra, dec)
            height_degrees: Height of rectangle (degrees)
            width_degrees: Width of rectangle (degrees)
            style: Style of rectangle
            angle: Angle of rotation clockwise (degrees)
            legend_label: Label for this object in the legend
        """
        points = geod.rectangle(
            center,
            height_degrees,
            width_degrees,
            angle,
        )
        self._polygon(points, style, gid=kwargs.get("gid") or "polygon")

        if legend_label is not None:
            self._add_legend_handle_marker(
                legend_label,
                style=style.to_marker_style(symbol=MarkerSymbolEnum.SQUARE),
            )

    @use_style(PolygonStyle)
    def ellipse(
        self,
        center: tuple,
        height_degrees: float,
        width_degrees: float,
        style: PolygonStyle,
        angle: float = 0,
        num_pts: int = 100,
        start_angle: int = 0,
        end_angle: int = 360,
        legend_label: str = None,
        **kwargs,
    ):
        """Plots an ellipse

        Args:
            center: Center of ellipse (ra, dec)
            height_degrees: Height of ellipse (degrees)
            width_degrees: Width of ellipse (degrees)
            style: Style of ellipse
            angle: Angle of rotation clockwise (degrees)
            num_pts: Number of points to calculate for the ellipse polygon
            start_angle: Angle to start at
            end_angle: Angle to end at
            legend_label: Label for this object in the legend
        """

        points = geod.ellipse(
            center,
            height_degrees,
            width_degrees,
            angle,
            num_pts,
            start_angle,
            end_angle,
        )
        self._polygon(points, style, gid=kwargs.get("gid") or "polygon")

        if legend_label is not None:
            self._add_legend_handle_marker(
                legend_label,
                style=style.to_marker_style(symbol=MarkerSymbolEnum.ELLIPSE),
            )

    @use_style(PolygonStyle)
    def circle(
        self,
        center: tuple,
        radius_degrees: float,
        style: PolygonStyle,
        num_pts: int = 100,
        legend_label: str = None,
        **kwargs,
    ):
        """Plots a circle

        Args:
            center: Center of circle (ra, dec)
            radius_degrees: Radius of circle (degrees)
            style: Style of circle
            num_pts: Number of points to calculate for the circle polygon
            legend_label: Label for this object in the legend
        """
        self.ellipse(
            center,
            radius_degrees * 2,
            radius_degrees * 2,
            style=style,
            angle=0,
            num_pts=num_pts,
            gid=kwargs.get("gid") or "polygon",
        )

        if legend_label is not None:
            self._add_legend_handle_marker(
                legend_label,
                style=style.to_marker_style(symbol=MarkerSymbolEnum.CIRCLE),
            )

    @use_style(LineStyle)
    def line(self, coordinates: list[tuple[float, float]], style: LineStyle, **kwargs):
        """Plots a line

        Args:
            coordinates: List of coordinates, e.g. `[(ra, dec), (ra, dec)]`
            style: Style of the line
        """
        x, y = zip(*[self._prepare_coords(*p) for p in coordinates])

        self.ax.plot(
            x,
            y,
            clip_on=True,
            clip_path=self._background_clip_path,
            gid=kwargs.get("gid") or "line",
            **style.matplot_kwargs(self.scale),
            **self._plot_kwargs(),
        )

    @use_style(ObjectStyle, "moon")
    def moon(
        self,
        style: ObjectStyle = None,
        true_size: bool = False,
        show_phase: bool = False,
        label: str = "Moon",
        legend_label: str = "Moon",
    ) -> None:
        """
        Plots the Moon.

        If you specified a lat/lon when creating the plot (e.g. for perspective projections or optic plots), then the Moon's _apparent_ RA/DEC will be calculated.

        Args:
            style: Styling of the Moon. If None, then the plot's style (specified when creating the plot) will be used
            true_size: If True, then the Moon's true apparent size in the sky will be plotted as a circle (the marker style's symbol will be ignored). If False, then the style's marker size will be used.
            show_phase: If True, and if `true_size = True`, then the approximate phase of the moon will be illustrated. The dark side of the moon will be colored with the marker's `edge_color`.
            label: How the Moon will be labeled on the plot and legend
        """
        m = models.Moon.get(
            dt=self.dt, lat=self.lat, lon=self.lon, ephemeris=self._ephemeris_name
        )
        m.name = label or m.name

        if not self.in_bounds(m.ra, m.dec):
            return

        self._objects.moon = m

        if true_size:
            # convert to PolygonStyle because we'll plot the true size as a polygon
            polygon_style = style.marker.to_polygon_style()

            # hide the edge because it can interfere with the true size
            polygon_style.edge_color = None

            if show_phase:
                self._moon_with_phase(
                    m.phase_description,
                    (m.ra, m.dec),
                    m.apparent_size,
                    style=polygon_style,
                    dark_side_color=style.marker.edge_color,
                )
            else:
                self.circle(
                    (m.ra, m.dec),
                    m.apparent_size,
                    style=polygon_style,
                    gid="moon-marker",
                )

            style.marker.symbol = MarkerSymbolEnum.CIRCLE
            self._add_legend_handle_marker(legend_label, style.marker)

            if label:
                self.text(label, m.ra, m.dec, style.label, gid="moon-label")

        else:
            self.marker(
                ra=m.ra,
                dec=m.dec,
                style=style,
                label=label,
                legend_label=legend_label,
                gid_marker="moon-marker",
                gid_label="moon-label",
            )

    def _moon_with_phase(
        self,
        moon_phase: MoonPhase,
        center: tuple,
        radius_degrees: float,
        style: PolygonStyle,
        dark_side_color: str,
        num_pts: int = 100,
    ):
        """
        Plots the (approximate) moon phase by drawing two half circles and one ellipse in the center,
        and then determining the color of each of the three shapes by the moon phase.
        """
        illuminated_color = style.fill_color

        left = style.copy()
        right = style.copy()
        middle = style.copy()

        if moon_phase == MoonPhase.WAXING_CRESCENT:
            left.fill_color = illuminated_color
            middle.fill_color = dark_side_color
            right.fill_color = dark_side_color

        elif moon_phase == MoonPhase.FIRST_QUARTER:
            left.fill_color = illuminated_color
            middle.alpha = 0
            right.fill_color = dark_side_color

        elif moon_phase == MoonPhase.WAXING_GIBBOUS:
            left.fill_color = illuminated_color
            middle.fill_color = illuminated_color
            right.fill_color = dark_side_color

        elif moon_phase == MoonPhase.FULL_MOON:
            left.fill_color = middle.fill_color = right.fill_color = illuminated_color

        elif moon_phase == MoonPhase.WANING_GIBBOUS:
            left.fill_color = dark_side_color
            middle.fill_color = illuminated_color
            right.fill_color = illuminated_color

        elif moon_phase == MoonPhase.LAST_QUARTER:
            left.fill_color = dark_side_color
            middle.alpha = 0
            right.fill_color = illuminated_color

        elif moon_phase == MoonPhase.WANING_CRESCENT:
            left.fill_color = dark_side_color
            middle.fill_color = dark_side_color
            right.fill_color = illuminated_color

        else:
            left.fill_color = middle.fill_color = right.fill_color = dark_side_color

        # Plot left side
        self.ellipse(
            center,
            radius_degrees * 2,
            radius_degrees * 2,
            style=left,
            num_pts=num_pts,
            angle=0,
            end_angle=180,  # plot as a semicircle
            gid="moon-marker",
        )
        # Plot right side
        self.ellipse(
            center,
            radius_degrees * 2,
            radius_degrees * 2,
            style=right,
            num_pts=num_pts,
            angle=180,
            end_angle=180,  # plot as a semicircle
            gid="moon-marker",
        )
        # Plot middle
        self.ellipse(
            center,
            radius_degrees * 2,
            radius_degrees,
            style=middle,
            gid="moon-marker",
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
            style=style,
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
            x0, y0 = self._prepare_coords(ra * 15, dec)
            x.append(x0)
            y.append(y0)
            if self.in_bounds(ra * 15, dec):
                inbounds.append((ra * 15, dec))

        self.ax.plot(
            x,
            y,
            dash_capstyle=style.line.dash_capstyle,
            clip_path=self._background_clip_path,
            gid="ecliptic-line",
            **style.line.matplot_kwargs(self.scale),
            **self._plot_kwargs(),
        )

        if label and len(inbounds) > 4:
            label_spacing = int(len(inbounds) / 4)

            for ra, dec in [inbounds[label_spacing], inbounds[label_spacing * 2]]:
                self.text(label, ra, dec, style.label, gid="ecliptic-label")

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

        for ra in range(25):
            x0, y0 = self._prepare_coords(ra * 15, 0)
            x.append(x0)
            y.append(y0)

        self.ax.plot(
            x,
            y,
            clip_path=self._background_clip_path,
            gid="celestial-equator-line",
            **style.line.matplot_kwargs(self.scale),
            **self._plot_kwargs(),
        )

        if label:
            label_spacing = (self.ra_max - self.ra_min) / 3
            for ra in np.arange(self.ra_min, self.ra_max, label_spacing):
                self.text(
                    label,
                    ra,
                    0.25,
                    style.label,
                    gid="celestial-equator-label",
                )
