import math
from dataclasses import dataclass

import numpy as np
import rtree
from shapely import Point, box
from shapely.errors import GEOSException
from matplotlib.text import Annotation

from starplot.config import settings as StarplotSettings, SvgTextType
from starplot.styles import AnchorPointEnum, LabelStyle
from starplot.styles.helpers import use_style
from starplot.geometry import (
    random_point_in_polygon_at_distance,
    union_at_zero,
)

"""
Long term strategy:

- plot all markers FIRST (but keep track of labels)
- on export, find best positions for labels
- introduce some "priority" for labels (e.g. order by)

"""

BBox = tuple[int, int, int, int]
"""Tuple of integers representing bounding box (xmin, ymin, xmax, ymax) -- in display coordinates."""


def round_away_from_zero(x):
    """
    Returns ceiling if number is greater than 0, else returns floor

    round_away_from_zero(5.1) -> 6
    round_away_from_zero(-5.1) -> -6

    """
    return math.ceil(x) if x > 0 else math.floor(x)


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

    attempts: int = 500
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

    def _is_clipped_box(self, bbox: BBox) -> bool:
        return not self._clip_path_polygon.contains(box(*bbox))

    def _get_label_bbox(self, label: Annotation) -> BBox:
        self.fig.draw_without_rendering()
        extent = label.get_window_extent(renderer=self.fig.canvas.get_renderer())
        result = (
            extent.xmin,
            extent.ymin,
            extent.xmax,
            extent.ymax,
        )
        if any([np.isnan(p) for p in result]):
            return None

        return tuple(int(p) for p in result)

    def _add_label_to_rtree(self, label: Annotation, bbox: BBox = None) -> None:
        """
        Adds a label to the R-Tree, which is a spatial index for all plotted labels and used for collision detection.

        If text debugging is enabled, then a white bounding box will be plotted around the label.

        Args:
            label: Annotation instance returned from matplotlib's annotate() function
            bbox: Tuple of integers representing bounding box (xmin, ymin, xmax, ymax) -- in display coordinates. If None, then bounding box will be obtained from label instance.
        """
        bbox = bbox or self._get_label_bbox(label)

        if self.debug_text:
            self._debug_bbox(bbox, color="white", width=1.5)

        self.labels.append(label)
        self._labels_rtree.insert(0, bbox)

    def _is_open_space(
        self,
        bbox: BBox,
        padding=0,
        allow_clipped=False,
        allow_label_collisions=False,
        allow_marker_collisions=False,
        allow_constellation_collisions=False,
    ) -> bool:
        """
        Returns true if the bounding box is in an open space, according to the allow_* kwargs.

        Args:
            bbox: Tuple of integers representing bounding box (xmin, ymin, xmax, ymax) -- in display coordinates.
        """
        x0, y0, x1, y1 = bbox
        bbox_padded = (
            x0 - padding,
            y0 - padding,
            x1 + padding,
            y1 + padding,
        )

        if any([np.isnan(c) for c in (x0, y0, x1, y1)]):
            return False

        if not allow_clipped and self._is_clipped_box(bbox_padded):
            return False

        if not allow_label_collisions and self._is_label_collision(bbox_padded):
            return False

        if not allow_marker_collisions and (
            self._is_star_collision(bbox_padded)
            or self._is_marker_collision(bbox_padded)
        ):
            return False

        if not allow_constellation_collisions and self._is_constellation_collision(
            bbox_padded
        ):
            return False

        return True

    def _text(self, x, y, text, **kwargs) -> Annotation:
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
    ) -> Annotation | None:
        if not text:
            return None

        x, y = self._prepare_coords(ra, dec)

        if StarplotSettings.svg_text_type == SvgTextType.PATH:
            kwargs["path_effects"] = kwargs.get("path_effects", [self.text_border])

        original_va = kwargs.pop("va", None)
        original_ha = kwargs.pop("ha", None)
        original_offset_x, original_offset_y = kwargs.pop("xytext", (0, 0))

        attempts = 0
        height = 0
        width = 0

        data_xy = self._proj.transform_point(x, y, self._crs)
        display_x, display_y = self.ax.transData.transform(data_xy)

        anchors = [(original_va, original_ha)]
        for a in collision_handler.anchor_fallbacks:
            d = AnchorPointEnum.from_str(a).as_matplot()
            anchors.append((d["va"], d["ha"]))

        for va, ha in anchors:
            attempts += 1
            offset_x, offset_y = original_offset_x, original_offset_y
            if original_ha != ha and ha != "center":
                offset_x *= -1

            if original_va != va:
                offset_y *= -1

            if ha == "center":
                offset_x = 0
                # offset_y *= 2

            # if va == "center":
            #     offset_x *= 2

            offset_x = round_away_from_zero(offset_x)
            offset_y = round_away_from_zero(offset_y)

            if height and width:
                offset_x_px = abs(offset_x * (self.dpi / 72))
                offset_y_px = abs(offset_y * (self.dpi / 72))

                if ha == "left":
                    x0 = int(display_x + offset_x_px)
                    x1 = int(display_x + offset_x_px + width)
                elif ha == "right":
                    x0 = int(display_x - offset_x_px - width)
                    x1 = int(display_x - offset_x_px)
                else:
                    x0 = int(display_x - offset_x_px - width / 2)
                    x1 = int(display_x + offset_x_px + width / 2)

                if va == "bottom":
                    # TOP
                    y0 = int(display_y + offset_y_px)
                    y1 = int(display_y + offset_y_px + height)
                elif va == "top":
                    # BOTTOM
                    y0 = int(display_y - offset_y_px - height)
                    y1 = int(display_y - offset_y_px)
                else:
                    # CENTER
                    y0 = int(display_y - height / 2) + offset_y
                    y1 = int(display_y + height / 2) + offset_y

                bbox = (x0, y0, x1, y1)
                label = None

            else:
                label = self._text(
                    x, y, text, va=va, ha=ha, xytext=(offset_x, offset_y), **kwargs
                )
                bbox = self._get_label_bbox(label)

                if bbox is None:
                    continue

                height = bbox[3] - bbox[1]
                width = bbox[2] - bbox[0]

            is_open = self._is_open_space(
                bbox,
                padding=0,
                allow_clipped=collision_handler.allow_clipped,
                allow_constellation_collisions=collision_handler.allow_constellation_line_collisions,
                allow_marker_collisions=collision_handler.allow_marker_collisions,
                allow_label_collisions=collision_handler.allow_label_collisions,
            )
            is_final_attempt = bool(
                (attempts == collision_handler.attempts) or (attempts == len(anchors))
            )

            if is_open or (collision_handler.plot_on_fail and is_final_attempt):
                label = label or self._text(
                    x, y, text, va=va, ha=ha, xytext=(offset_x, offset_y), **kwargs
                )
                self._add_label_to_rtree(label, bbox=bbox)
                return label

            if label is not None:
                label.remove()

            if is_final_attempt:
                return None

    def _text_area(
        self,
        ra: float,
        dec: float,
        text: str,
        area,
        collision_handler: CollisionHandler,
        **kwargs,
    ) -> Annotation | None:
        kwargs["va"] = "center"
        kwargs["ha"] = "center"

        if StarplotSettings.svg_text_type == SvgTextType.PATH:
            kwargs["path_effects"] = kwargs.get("path_effects", [self.text_border])

        padding = 0
        max_distance = 2_000
        distance_step_size = 2
        attempts = 0
        height = None
        width = None
        bbox = None

        origin = Point(ra, dec)

        total_area = (
            area
            if area.geom_type != "MultiPolygon"
            else union_at_zero(area.geoms[0], area.geoms[1])
        )
        original_size = total_area.area
        buffer = -0.05 if original_size < 400 else -1

        # Intersect with extent
        extent = self._extent_mask()

        try:
            area = area.intersection(extent)
        except GEOSException:
            # TODO : handle this better
            pass

        area = (
            area
            if area.geom_type != "MultiPolygon"
            else union_at_zero(area.geoms[0], area.geoms[1])
        )
        area = area.buffer(buffer, cap_style="square", join_style="mitre")

        if not area.contains(origin) or area.area < (original_size * 0.9):
            origin = area.centroid

        if self.debug_text and area.is_valid and not origin.is_empty:
            """Plots marker at origin and polygon of area"""
            self.marker(
                origin.x,
                origin.y,
                style={
                    "marker": {
                        "symbol": "triangle",
                        "color": "red",
                    }
                },
            )
            self.polygon(
                geometry=area,
                style={
                    "edge_color": "red",
                    "edge_width": 2,
                },
            )

        for d in range(0, max_distance, distance_step_size):
            attempts += 1

            if not area.contains(origin):
                continue
            distance = d / 25
            point = random_point_in_polygon_at_distance(
                area,
                origin_point=origin,
                distance=distance,
                max_iterations=10,
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

                if bbox is None:
                    continue

                height = bbox[3] - bbox[1]
                width = bbox[2] - bbox[0]

            is_open = self._is_open_space(
                bbox,
                padding=padding,
                allow_clipped=collision_handler.allow_clipped,
                allow_constellation_collisions=collision_handler.allow_constellation_line_collisions,
                allow_marker_collisions=collision_handler.allow_marker_collisions,
                allow_label_collisions=collision_handler.allow_label_collisions,
            )
            is_final_attempt = attempts == collision_handler.attempts

            # # TODO : remove label if not fully inside area?

            if is_open or (collision_handler.plot_on_fail and is_final_attempt):
                label = label or self._text(x, y, text, **kwargs)
                self._add_label_to_rtree(label, bbox=bbox)
                return label

            if label is not None:
                label.remove()

            if is_final_attempt:
                return None

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

        style = style.model_copy()  # need a copy because we possibly mutate it below

        collision_handler = collision_handler or self.collision_handler

        if style.offset_x == "auto":
            style.offset_x = 0

        if style.offset_y == "auto":
            style.offset_y = 0

        if kwargs.get("area"):
            label = self._text_area(
                ra,
                dec,
                text,
                **style.matplot_kwargs(self.scale),
                area=kwargs.pop("area"),
                collision_handler=collision_handler,
                xycoords="data",
                xytext=(
                    style.offset_x * self.scale,
                    style.offset_y * self.scale,
                ),
                textcoords="offset points",
                **kwargs,
            )
        else:
            label = self._text_point(
                ra,
                dec,
                text,
                **style.matplot_kwargs(self.scale),
                collision_handler=collision_handler,
                xycoords="data",
                xytext=(
                    style.offset_x * self.scale,
                    style.offset_y * self.scale,
                ),
                textcoords="offset points",
                **kwargs,
            )

        if self.debug_text and label:
            """Plots RED box around actual position of label"""
            bbox = self._get_label_bbox(label)
            self._debug_bbox(bbox, color="red", width=1)

        return label
