from dataclasses import dataclass
from random import randrange

import numpy as np
import rtree
from shapely import Point
from matplotlib.text import Text

from starplot.config import settings as StarplotSettings, SvgTextType
from starplot.styles import AnchorPointEnum, LabelStyle
from starplot.styles.helpers import use_style
from starplot.geometry import (
    unwrap_polygon_360,
    random_point_in_polygon_at_distance,
)

"""
Long term strategy:

- plot all markers FIRST (but keep track of labels)
- on export, find best positions for labels
- introduce some "priority" for labels (e.g. order by)

"""

BBox = tuple[float, float, float, float]


@dataclass
class CollisionHandler:
    """
    Dataclass that describes how to handle label collisions with other objects, like text, markers, constellation lines, etc.
    """

    allow_clipped: bool = False
    """If True, then labels will be plotted if they're clipped (i.e. part of the label is outside the plot area)"""

    allow_label_collisions: bool = False
    """If True, then labels will be plotted if they collide with another label"""

    allow_marker_collisions: bool = False
    """If True, then labels will be plotted if they collide with another marker"""

    allow_constellation_line_collisions: bool = False
    """If True, then labels will be plotted if they collide with a constellation line"""

    plot_on_fail: bool = False
    """If True, then labels will be plotted even if no allowed position is found. They will be plotted at their last attempted position."""

    attempts: int = 10
    """Max attempts to find a good label position"""

    seed: int = None
    """Random seed for randomly generating points"""

    anchor_fallbacks: list[AnchorPointEnum] = None
    """
    If a point-based label's preferred anchor point results in a collision, then these fallbacks will be tried in 
    sequence until a collision-free position is found.

    Default:
    ```python
    [
        AnchorPointEnum.BOTTOM_RIGHT,
        AnchorPointEnum.TOP_LEFT,
        AnchorPointEnum.TOP_RIGHT,
        AnchorPointEnum.BOTTOM_LEFT,
        AnchorPointEnum.BOTTOM_CENTER,
        AnchorPointEnum.TOP_CENTER,
        AnchorPointEnum.RIGHT_CENTER,
        AnchorPointEnum.LEFT_CENTER,
    ]
    ```
    """

    def __post_init__(self):
        self.anchor_fallbacks = self.anchor_fallbacks or [
            AnchorPointEnum.BOTTOM_RIGHT,
            AnchorPointEnum.TOP_LEFT,
            AnchorPointEnum.TOP_RIGHT,
            AnchorPointEnum.BOTTOM_LEFT,
            AnchorPointEnum.BOTTOM_CENTER,
            AnchorPointEnum.TOP_CENTER,
            AnchorPointEnum.RIGHT_CENTER,
            AnchorPointEnum.LEFT_CENTER,
        ]


class TextPlotterMixin:
    def __init__(self, *args, **kwargs):
        self.labels = []
        self._labels_rtree = rtree.index.Index()
        self._constellations_rtree = rtree.index.Index()
        self._stars_rtree = rtree.index.Index()
        self._markers_rtree = rtree.index.Index()
        self.collision_handler = kwargs.pop("collision_handler", CollisionHandler())

    def _is_label_collision(self, bbox: BBox) -> bool:
        ix = list(self._labels_rtree.intersection(bbox))
        return len(ix) > 0

    def _is_constellation_collision(self, bbox: BBox) -> bool:
        ix = list(self._constellations_rtree.intersection(bbox))
        return len(ix) > 0

    def _is_star_collision(self, bbox: BBox) -> bool:
        ix = list(self._stars_rtree.intersection(bbox))
        return len(ix) > 0

    def _is_marker_collision(self, bbox: BBox) -> bool:
        ix = list(self._markers_rtree.intersection(bbox))
        return len(ix) > 0

    def _is_clipped(self, points) -> bool:
        p = self._clip_path_polygon

        for x, y in points:
            if not p.contains(Point(x, y)):
                return True

        return False

    def _add_label_to_rtree(self, label: Text, extent=None):
        extent = extent or label.get_window_extent(
            renderer=self.fig.canvas.get_renderer()
        )
        self.labels.append(label)
        self._labels_rtree.insert(
            0, np.array((extent.x0 - 1, extent.y0 - 1, extent.x1 + 1, extent.y1 + 1))
        )

    def _is_open_space(
        self,
        bbox: BBox,
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

    def _get_label_bbox(self, label: Text) -> BBox:
        extent = label.get_window_extent(renderer=self.fig.canvas.get_renderer())
        return (extent.x0, extent.y0, extent.x1, extent.y1)

    def _maybe_remove_label(
        self,
        label: Text,
        collision_handler: CollisionHandler,
    ) -> bool:
        """Returns true if the label is removed, else false"""
        extent = label.get_window_extent(renderer=self.fig.canvas.get_renderer())
        bbox = self._get_label_bbox(label)
        points = [(extent.x0, extent.y0), (extent.x1, extent.y1)]

        if any([np.isnan(c) for c in bbox]):
            label.remove()
            return True

        if not collision_handler.allow_clipped and self._is_clipped(points):
            label.remove()
            return True

        if not collision_handler.allow_label_collisions and self._is_label_collision(
            bbox
        ):
            label.remove()
            return True

        if not collision_handler.allow_marker_collisions and (
            self._is_star_collision(bbox) or self._is_marker_collision(bbox)
        ):
            label.remove()
            return True

        if (
            not collision_handler.allow_constellation_line_collisions
            and self._is_constellation_collision(bbox)
        ):
            label.remove()
            return True

        return False

    def _text(self, x, y, text, **kwargs) -> Text:
        """Plots text at (x, y)"""
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
        collision_handler: CollisionHandler,
        **kwargs,
    ) -> Text | None:
        if not text:
            return None

        x, y = self._prepare_coords(ra, dec)

        if StarplotSettings.svg_text_type == SvgTextType.PATH:
            kwargs["path_effects"] = kwargs.get("path_effects", [self.text_border])

        original_va = kwargs.pop("va", None)
        original_ha = kwargs.pop("ha", None)
        original_offset_x, original_offset_y = kwargs.pop("xytext", (0, 0))

        anchors = [(original_va, original_ha)]
        for a in collision_handler.anchor_fallbacks:
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
                x, y, text, va=va, ha=ha, xytext=(offset_x, offset_y), **kwargs
            )
            removed = self._maybe_remove_label(label, collision_handler)

            if collision_handler.plot_on_fail or not removed:
                self._add_label_to_rtree(label)
                return label

    def _text_area(
        self,
        ra: float,
        dec: float,
        text: str,
        area,
        collision_handler: CollisionHandler,
        **kwargs,
    ) -> Text | None:
        kwargs["va"] = "center"
        kwargs["ha"] = "center"

        if StarplotSettings.svg_text_type == SvgTextType.PATH:
            kwargs["path_effects"] = kwargs.get("path_effects", [self.text_border])

        padding = 6
        max_distance = 3_000
        distance_step_size = 2
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
                max_iterations=collision_handler.attempts,
                seed=collision_handler.seed,
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
                avoid_clipped=not collision_handler.allow_clipped,
                avoid_constellation_collision=not collision_handler.allow_constellation_line_collisions,
                avoid_marker_collisions=not collision_handler.allow_marker_collisions,
                avoid_label_collisions=not collision_handler.allow_label_collisions,
            )

            # # TODO : remove label if not fully inside area?

            attempts += 1

            if is_open and label is None:
                label = self._text(x, y, text, **kwargs)

            if is_open or (
                collision_handler.plot_on_fail
                and attempts == collision_handler.attempts
            ):
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
        collision_handler: CollisionHandler = None,
        **kwargs,
    ):
        """
        Plots text

        Args:
            text: Text to plot
            ra: Right ascension of text (0...360)
            dec: Declination of text (-90...90)
            style: Styling of the text
            collision_handler: An instance of [CollisionHandler][starplot.CollisionHandler] that describes what to do on collisions with other labels, markers, etc. If `None`, then the collision handler of the plot will be used.
        """
        if not text:
            return

        style = style or LabelStyle()
        collision_handler = collision_handler or self.collision_handler

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
                collision_handler=collision_handler,
                xycoords="data",
                xytext=(style.offset_x * self.scale, style.offset_y * self.scale),
                textcoords="offset points",
                **kwargs,
            )
        else:
            return self._text_point(
                ra,
                dec,
                text,
                **style.matplot_kwargs(self.scale),
                collision_handler=collision_handler,
                xycoords="data",
                xytext=(style.offset_x * self.scale, style.offset_y * self.scale),
                textcoords="offset points",
                **kwargs,
            )
