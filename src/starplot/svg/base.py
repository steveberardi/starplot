from abc import ABC, abstractmethod
from typing import Dict, Union, Optional
import logging

import rtree
import numpy as np
from matplotlib import patches
from matplotlib.lines import Line2D
from shapely import Polygon, LineString

from starplot.coordinates import CoordinateSystem
from starplot import models, warnings
from starplot import geometry as _geometry
from starplot.config import settings as StarplotSettings, SvgTextType
from starplot.data import load, ecliptic
from starplot.data.translations import translate
from starplot.models.planet import PlanetName, PLANET_LABELS_DEFAULT
from starplot.models.moon import MoonPhase
from starplot.models.optics import Optic, Camera
from starplot.models.observer import Observer
from starplot.styles import (
    PlotStyle,
    MarkerStyle,
    ObjectStyle,
    LabelStyle,
    MarkerSymbolEnum,
    PathStyle,
    PolygonStyle,
    GradientDirection,
    fonts,
    AnchorPointEnum,
)
from starplot.projections import ProjectionBase
from starplot.plotters import StarPlotterMixinSVG
from starplot.plotters.debug import DebugPlotterMixin
from starplot.plotters.text import TextPlotterMixin, CollisionHandler
from starplot.styles.helpers import use_style
from starplot.profile import profile
from starplot.svg.canvas import Canvas

LOGGER = logging.getLogger("starplot-svg")
LOG_HANDLER = logging.StreamHandler()
LOG_FORMATTER = logging.Formatter(
    "\033[1;34m%(name)s\033[0m:[%(levelname)s]: %(message)s"
)
LOG_HANDLER.setFormatter(LOG_FORMATTER)
LOGGER.addHandler(LOG_HANDLER)

DEFAULT_RESOLUTION = 4096


class BasePlot(StarPlotterMixinSVG, ABC):
    _background_clip_path = None
    _clip_path_polygon: Polygon = None  # clip path in display coordinates
    _coordinate_system = CoordinateSystem.RA_DEC
    _gradient_direction: GradientDirection = GradientDirection.LINEAR

    canvas: Canvas

    style: PlotStyle
    """
    The plot's style.
    """

    point_label_handler: CollisionHandler
    """Default [collision handler][starplot.CollisionHandler] for point labels."""

    area_label_handler: CollisionHandler
    """Default [collision handler][starplot.CollisionHandler] for area labels."""

    path_label_handler: CollisionHandler
    """Default [collision handler][starplot.CollisionHandler] for path labels."""

    def __init__(
        self,
        observer: Observer = None,
        ephemeris: str = "de440s.bsp",
        style: PlotStyle = None,
        resolution: int = 4096,
        point_label_handler: CollisionHandler = None,
        area_label_handler: CollisionHandler = None,
        path_label_handler: CollisionHandler = None,
        scale: float = 1.0,
        autoscale: bool = False,
        suppress_warnings: bool = True,
        # new for canvas backend
        projection: ProjectionBase = None,
        bounds: tuple[float, float, float, float] = None,
        invert_x: bool = False,
        invert_y: bool = False,
        clip_path=None,
        *args,
        **kwargs,
    ):
        # super().__init__(*args, **kwargs)

        self.labels = []
        self._labels_rtree = rtree.index.Index()
        self._constellations_rtree = rtree.index.Index()
        self._stars_rtree = rtree.index.Index()
        self._markers_rtree = rtree.index.Index()

        self.language = StarplotSettings.language

        self.style = style or PlotStyle()
        self.resolution = resolution

        self.scale = scale
        self.autoscale = autoscale
        if self.autoscale:
            self.scale = self.resolution / DEFAULT_RESOLUTION

        self.scale *= 1.28

        self.debug = StarplotSettings.debug or bool(kwargs.get("debug"))
        self.debug_text = StarplotSettings.debug or bool(kwargs.get("debug_text"))
        self.log_level = logging.DEBUG if self.debug else logging.ERROR
        self.logger = LOGGER
        self.logger.setLevel(self.log_level)

        self.canvas = Canvas(
            resolution=resolution,
            style=self.style,
            scale=self.scale,
            projection=projection,
            bounds=bounds,
            clip_path=None,
            invert_x=invert_x,
            invert_y=invert_y,
            suppress_warnings=suppress_warnings,
            logger=LOGGER,
        )
        self.projection = projection

        self._background_clip_path = None
        self._legend = None
        self._legend_handles = {}

        self.point_label_handler = point_label_handler or CollisionHandler(
            attempts=10,
            anchor_fallbacks=[
                AnchorPointEnum.BOTTOM_RIGHT,
                AnchorPointEnum.TOP_LEFT,
                AnchorPointEnum.TOP_RIGHT,
                AnchorPointEnum.BOTTOM_LEFT,
                AnchorPointEnum.BOTTOM_CENTER,
                AnchorPointEnum.TOP_CENTER,
                AnchorPointEnum.RIGHT_CENTER,
                AnchorPointEnum.LEFT_CENTER,
            ],
        )
        self.area_label_handler = area_label_handler or CollisionHandler(
            allow_constellation_line_collisions=True
        )
        self.path_label_handler = path_label_handler or CollisionHandler(
            allow_constellation_line_collisions=True
        )

        self.observer = observer or Observer()
        self.ephemeris_name = ephemeris
        self.ephemeris = load(ephemeris)
        self.earth = self.ephemeris["earth"]

        self._objects = models.ObjectList()
        self._labeled_stars = []

    def _plot_kwargs(self) -> dict:
        return {}

    def _prepare_coords(self, ra, dec) -> tuple[float, float]:
        return ra, dec

    def _prepare_coords_many(self, coordinates: list, epoch_year: float = 2000) -> list:
        return coordinates

    def _update_clip_path_polygon(self, buffer=8):
        self.fig.draw_without_rendering()
        coords = self._background_clip_path.get_verts()
        self._clip_path_polygon = Polygon(coords).buffer(-1 * buffer)

        # if self.debug_text:
        #     patch = patches.Polygon(
        #         Polygon(coords).buffer(-1 * buffer).exterior.coords,
        #         fill=False,
        #         facecolor="none",
        #         edgecolor="red",
        #         linewidth=4,
        #         zorder=5_000,
        #         transform=None,
        #     )
        #     self.ax.add_patch(patch)

    def _add_legend_handle_marker(self, label: str, style: MarkerStyle):
        return
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

    @property
    def magnitude_range(self) -> tuple[float, float]:
        """
        Range of magnitude for all plotted stars, as a tuple (min, max)
        """
        mags = [s.magnitude for s in self.objects.stars]
        return (min(mags), max(mags))

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
        self.canvas.title(text, style)

    @profile
    def export(self, filename: str):
        """Exports the plot to an image file.

        Args:
            filename: Filename of exported file (the format will be inferred from the extension)

        """
        self.logger.debug("Exporting...")
        self.canvas.export(filename)

    @use_style(ObjectStyle)
    def marker(
        self,
        ra: float,
        dec: float,
        style: Union[dict, ObjectStyle],
        label: Optional[str] = None,
        legend_label: str = None,
        skip_bounds_check: bool = False,
        collision_handler: CollisionHandler = None,
        gid: str = None,
    ) -> None:
        """Plots a marker

        Args:
            ra: Right ascension of the marker
            dec: Declination of the marker
            label: Label for the marker
            style: Styling for the marker
            legend_label: How to label the marker in the legend. If `None`, then the marker will not be added to the legend
            skip_bounds_check: If True, then don't check the marker coordinates to ensure they're within the bounds of the plot. If you're plotting many markers, setting this to True can speed up plotting time.
            collision_handler: An instance of [CollisionHandler][starplot.CollisionHandler] that describes what to do on label collisions with other labels, markers, etc. If `None`, then the collision handler of the plot will be used.

        """

        if not skip_bounds_check and not self.in_bounds(ra, dec):
            return

        x, y = self._prepare_coords(ra, dec)

        self.canvas.marker(
            x,
            y,
            style=style.marker,
            # gid=gid or "marker",
        )

        # Add to spatial index
        display_x, display_y = self.canvas._to_display(x, y)
        if display_x > 0 and display_y > 0:
            radius = style.marker.size * self.scale
            bbox = np.array(
                (
                    display_x - radius,
                    display_y - radius,
                    display_x + radius,
                    display_y + radius,
                )
            )
            self._markers_rtree.insert(0, bbox, None)

        return

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
                collision_handler=collision_handler or self.point_label_handler,
                gid=kwargs.get("gid_label") or "marker-label",
            )

        if legend_label is not None:
            self._legend_handles[legend_label] = result

    @use_style(ObjectStyle, "planets")
    def planets(
        self,
        style: ObjectStyle = None,
        true_size: bool = False,
        labels: Dict[PlanetName, str] = PLANET_LABELS_DEFAULT,
        legend_label: str = "Planet",
        collision_handler: CollisionHandler = None,
    ) -> None:
        """
        Plots the planets, at their _apparent_ RA/DEC (based on the observer you defined).

        Args:
            style: Styling of the planets. If None, then the plot's style (specified when creating the plot) will be used
            true_size: If True, then each planet's true apparent size in the sky will be plotted. If False, then the style's marker size will be used.
            labels: How the planets will be labeled on the plot and legend. If not specified, then the planet's name will be used (see [`Planet`][starplot.models.planet.PlanetName])
            legend_label: How to label the planets in the legend. If `None`, then the planets will not be added to the legend
            collision_handler: An instance of [CollisionHandler][starplot.CollisionHandler] that describes what to do on label collisions with other labels, markers, etc. If `None`, then the collision handler of the plot will be used.
        """
        labels = labels or {}
        planets = models.Planet.all(self.observer, self.ephemeris_name)

        legend_label = translate(legend_label, self.language)
        handler = collision_handler or self.point_label_handler

        for p in planets:
            label = labels.get(p.name)
            label = translate(label, self.language)

            if self.in_bounds(p.ra, p.dec):
                self._objects.planets.append(p)

            if true_size:
                polygon_style = style.marker.to_polygon_style()
                polygon_style.edge_color = None
                self.circle(
                    center=(p.ra, p.dec),
                    radius_degrees=p.apparent_size / 2,
                    style=polygon_style,
                    gid="planet-marker",
                )
                self._add_legend_handle_marker(legend_label, style.marker)

                if label:
                    self.text(
                        label.upper(),
                        p.ra,
                        p.dec,
                        style.label,
                        collision_handler=handler,
                        gid="planet-label",
                    )
            else:
                self.marker(
                    ra=p.ra,
                    dec=p.dec,
                    style=style,
                    label=label.upper() if label else None,
                    legend_label=legend_label,
                    collision_handler=handler,
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
        collision_handler: CollisionHandler = None,
    ) -> None:
        """
        Plots the Sun, at its _apparent_ RA/DEC (based on the observer you defined).

        Args:
            style: Styling of the Sun. If None, then the plot's style (specified when creating the plot) will be used
            true_size: If True, then the Sun's true apparent size in the sky will be plotted as a circle (the marker style's symbol will be ignored). If False, then the style's marker size will be used.
            label: How the Sun will be labeled on the plot
            legend_label: How the sun will be labeled in the legend
            collision_handler: An instance of [CollisionHandler][starplot.CollisionHandler] that describes what to do on label collisions with other labels, markers, etc. If `None`, then the collision handler of the plot will be used.
        """
        s = models.Sun.get(
            observer=self.observer,
            ephemeris=self.ephemeris_name,
        )
        label = translate(label, self.language)
        legend_label = translate(legend_label, self.language)
        s.name = label or s.name
        handler = collision_handler or self.point_label_handler

        if not self.in_bounds(s.ra, s.dec):
            return

        self._objects.sun = s

        if true_size:
            polygon_style = style.marker.to_polygon_style()

            # hide the edge because it can interfere with the true size
            polygon_style.edge_color = None

            self.circle(
                center=(s.ra, s.dec),
                radius_degrees=s.apparent_size / 2,
                style=polygon_style,
                gid="sun-marker",
                num_pts=200,
            )

            style.marker.symbol = MarkerSymbolEnum.CIRCLE
            self._add_legend_handle_marker(legend_label, style.marker)

            if label:
                self.text(
                    label,
                    s.ra,
                    s.dec,
                    style.label,
                    collision_handler=handler,
                    gid="sun-label",
                )

        else:
            self.marker(
                ra=s.ra,
                dec=s.dec,
                style=style,
                label=label,
                legend_label=legend_label,
                collision_handler=handler,
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
        points = self._prepare_coords_many(points)
        self.canvas.polygon(points, style)

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

        self._polygon(points, style, gid=kwargs.get("gid") or "polygon", **kwargs)

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
        polygon = _geometry.rectangle(
            center,
            height_degrees,
            width_degrees,
            angle,
        )
        polygon = polygon.segmentize(0.1)
        points = list(zip(*polygon.exterior.coords.xy))
        self._polygon(points, style, gid=kwargs.get("gid") or "polygon")

        # if legend_label is not None:
        #     self._add_legend_handle_marker(
        #         legend_label,
        #         style=style.to_marker_style(symbol=MarkerSymbolEnum.SQUARE),
        #     )

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

        polygon = _geometry.ellipse(
            center,
            height_degrees,
            width_degrees,
            angle,
            num_pts,
            start_angle,
            end_angle,
        )
        points = list(zip(*polygon.exterior.coords.xy))
        self._polygon(points, style, gid=kwargs.get("gid") or "polygon")

        # if legend_label is not None:
        #     self._add_legend_handle_marker(
        #         legend_label,
        #         style=style.to_marker_style(symbol=MarkerSymbolEnum.ELLIPSE),
        #     )

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

        # if legend_label is not None:
        #     self._add_legend_handle_marker(
        #         legend_label,
        #         style=style.to_marker_style(symbol=MarkerSymbolEnum.CIRCLE),
        #     )

    @use_style(ObjectStyle, "moon")
    def moon(
        self,
        style: ObjectStyle = None,
        true_size: bool = False,
        show_phase: bool = False,
        label: str = "Moon",
        legend_label: str = "Moon",
        collision_handler: CollisionHandler = None,
    ) -> None:
        """
        Plots the Moon, at its _apparent_ RA/DEC (based on the observer you defined).

        Args:
            style: Styling of the Moon. If None, then the plot's style (specified when creating the plot) will be used
            true_size: If True, then the Moon's true apparent size in the sky will be plotted as a circle (the marker style's symbol will be ignored). If False, then the style's marker size will be used.
            show_phase: If True, and if `true_size = True`, then the phase of the moon will be illustrated. The dark side of the moon will be colored with the marker's `edge_color`.
            label: How the Moon will be labeled on the plot
            legend_label: How the Moon will be labeled in the legend
            collision_handler: An instance of [CollisionHandler][starplot.CollisionHandler] that describes what to do on label collisions with other labels, markers, etc. If `None`, then the collision handler of the plot will be used.
        """
        m = models.Moon.get(
            observer=self.observer,
            ephemeris=self.ephemeris_name,
        )
        label = translate(label, self.language)
        legend_label = translate(legend_label, self.language)
        m.name = label or m.name
        handler = collision_handler or self.point_label_handler

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
                    moon_phase=m.phase_description,
                    center=(m.ra, m.dec),
                    radius_degrees=m.apparent_size / 2,
                    style=polygon_style,
                    dark_side_color=style.marker.edge_color,
                )
            else:
                self.circle(
                    center=(m.ra, m.dec),
                    radius_degrees=m.apparent_size / 2,
                    style=polygon_style,
                    gid="moon-marker",
                )

            style.marker.symbol = MarkerSymbolEnum.CIRCLE
            self._add_legend_handle_marker(legend_label, style.marker)

            if label:
                self.text(
                    label,
                    m.ra,
                    m.dec,
                    style.label,
                    collision_handler=handler,
                    gid="moon-label",
                )

        else:
            self.marker(
                ra=m.ra,
                dec=m.dec,
                style=style,
                label=label,
                legend_label=legend_label,
                collision_handler=handler,
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
        num_pts: int = 200,
    ):
        """
        Plots the (approximate) moon phase by drawing two half circles and one ellipse in the center,
        and then determining the color of each of the three shapes by the moon phase.
        """
        illuminated_color = style.fill_color

        ellipse_b_radius_degrees = np.abs(
            radius_degrees * (2 * self._objects.moon.illumination - 1)
        )

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
            height_degrees=radius_degrees * 2,
            width_degrees=radius_degrees * 2,
            style=left,
            num_pts=num_pts,
            angle=0,
            end_angle=180,  # plot as a semicircle
            gid="moon-marker",
        )
        # Plot right side
        self.ellipse(
            center,
            height_degrees=radius_degrees * 2,
            width_degrees=radius_degrees * 2,
            style=right,
            num_pts=num_pts,
            angle=180,
            end_angle=180,  # plot as a semicircle
            gid="moon-marker",
        )
        # Plot middle
        self.ellipse(
            center,
            height_degrees=radius_degrees * 2,
            width_degrees=ellipse_b_radius_degrees * 2,
            num_pts=num_pts,
            style=middle,
            gid="moon-marker",
        )

    @use_style(PolygonStyle, "optic_fov")
    def optic_fov(
        self,
        ra: float,
        dec: float,
        optic: Optic,
        style: PolygonStyle = None,
    ):
        """Draws a polygon representing the field of view for an optic, centered at a specific point.

        Args:
            ra: Right ascension of the center of view
            dec: Declination of the center of view
            optic: Instance of an [Optic][starplot.models.Optic]
            style: style of the polygon
        """
        if isinstance(optic, Camera):
            self.rectangle(
                center=(ra, dec),
                height_degrees=optic.true_fov_y,
                width_degrees=optic.true_fov_x,
                angle=optic.rotation,
                style=style,
            )
        else:
            self.circle(
                center=(ra, dec),
                radius_degrees=optic.true_fov / 2,
                style=style,
            )

    @profile
    @use_style(PathStyle, "ecliptic")
    def ecliptic(
        self,
        style: PathStyle = None,
        label: str = "ECLIPTIC",
        num_labels: int = 2,
        collision_handler: CollisionHandler = None,
    ):
        """Plots the ecliptic

        Args:
            style: Styling of the ecliptic. If None, then the plot's style will be used
            label: How the ecliptic will be labeled on the plot
            num_labels: Max number of labels to plot along the line
            collision_handler: An instance of [CollisionHandler][starplot.CollisionHandler] that describes what to do on label collisions with other labels, markers, etc. If `None`, then the plot's `path_label_handler` will be used.
        """

        label = translate(label, self.language)
        coords = [(ra * 15, dec) for ra, dec in ecliptic.RA_DECS]

        self.line(
            style=style,
            label=label.upper(),
            num_labels=num_labels,
            collision_handler=collision_handler,
            coordinates=coords,
        )

    @profile
    @use_style(PathStyle, "celestial_equator")
    def celestial_equator(
        self,
        style: PathStyle = None,
        label: str = "CELESTIAL EQUATOR",
        num_labels: int = 2,
        collision_handler: CollisionHandler = None,
    ):
        """
        Plots the celestial equator

        Args:
            style: Styling of the celestial equator. If None, then the plot's style will be used
            label: How the celestial equator will be labeled on the plot
            num_labels: Max number of labels to plot along the line
            collision_handler: An instance of [CollisionHandler][starplot.CollisionHandler] that describes what to do on label collisions with other labels, markers, etc. If `None`, then the plot's `path_label_handler` will be used.
        """
        label = translate(label, self.language)
        coords = [(ra, 0) for ra in range(0, 361)]
        self.line(
            style=style,
            label=label.upper(),
            num_labels=num_labels,
            collision_handler=collision_handler,
            coordinates=coords,
            # gid="celestial-equator",
        )

    @use_style(PathStyle)
    def line(
        self,
        coordinates: list[tuple[float, float]] = None,
        geometry: LineString = None,
        style: PathStyle = None,
        label: str = None,
        num_labels: int = 2,
        collision_handler: CollisionHandler = None,
        **kwargs,
    ):
        """Plots a line, with optional labels. Either coordinates OR geometry must be specified.

        Args:

            coordinates: List of coordinates, e.g. `[(ra, dec), (ra, dec)]`
            geometry: A shapely LineString. If this value is passed, then the `coordinates` kwarg will be ignored.
            style: Style of the line
            label: Label for the line
            num_labels: Number of labels to plot along the line
            collision_handler: An instance of [CollisionHandler][starplot.CollisionHandler] that describes what to do on label collisions with other labels, markers, etc. If `None`, then the plot's `path_label_handler` will be used.

        """

        if coordinates is None and geometry is None:
            raise ValueError("Must pass coordinates or geometry when plotting lines.")

        coords = geometry.coords if geometry is not None else coordinates
        prepared_coords = [self._prepare_coords(*p) for p in coords]
        x, y = zip(*prepared_coords)

        gid = kwargs.get("gid") or "line"

        collision_handler = collision_handler or self.path_label_handler

        self.canvas.line(
            style=style,
            label=label,
            num_labels=num_labels,
            collision_handler=collision_handler,
            coordinates=coords,
            # gid="celestial-equator",
        )

        if label:
            arr = np.array(coordinates)
            xs, ys = arr[:, 0], arr[:, 1]
            self._text_line(
                xs,
                ys,
                text=label,
                style=style.label,
                num_labels=num_labels,
                collision_handler=collision_handler,
            )

        # if not label:
        #     return

        # prepared_coords = [
        #     (x, y) for x, y in prepared_coords if self._in_bounds_xy(x, y)
        # ]

        # if not prepared_coords:
        #     return

        # x, y = zip(*prepared_coords)

        # collision_handler = collision_handler or self.path_label_handler

        # self._text_line(
        #     x,
        #     y,
        #     label,
        #     num_labels=num_labels,
        #     collision_handler=collision_handler,
        #     min_spacing=0.65,
        #     **style.label.matplot_kwargs(self.scale),
        #     **self._plot_kwargs(),
        #     clip_path=self._background_clip_path,
        #     gid=gid,
        # )

    def _debug_bbox(self, bbox, color, width=1):
        x0, y0, x1, y1 = bbox
        self.canvas._rectangle(
            x=x0,
            y=y0,
            height=y1 - y0,
            width=x1 - x0,
            color=color,
            stroke_width=width,
        )
