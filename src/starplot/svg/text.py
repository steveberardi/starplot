import math
from dataclasses import dataclass

import numpy as np
import rtree
from shapely import Point, box
from shapely.errors import GEOSException

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


def next_best_position(
    plotted_positions: list[int],
    available_positions: list[int],
    num_labels: int,
    num_positions: int,
) -> int:
    """
    Returns the next best (evenly spaced) position based on distance from plotted positions

    Assumes original positions are evenly spaced on line

    Args:
        plotted_positions: List of indices of plotted label positions on the line
        available_positions: List of available positions to plot labels
        num_labels: Number of labels to be plotted on the line
        num_positions: Original number of positions that were available

    Returns:
        Next best (evenly spaced) position (the index from original list of coordinates)
    """

    if len(plotted_positions) == 0:
        return available_positions[len(available_positions) // (num_labels + 1)]

    positions = [0] + sorted(plotted_positions) + [num_positions - 1]
    diffs = [positions[i] - positions[i - 1] for i in range(1, len(positions))]
    avg = sum(diffs) / len(diffs)

    # filter out available positions that are too close to plotted positions
    # (i.e. closer than average distance)
    possible = []
    for p in available_positions:
        min_distance = min([abs(plotted - p) for plotted in plotted_positions])
        if min_distance >= avg * 0.9:
            possible.append((min_distance, p))

    if not possible:
        return None

    possible.sort()

    return possible[0][1]


def rotate_bbox(bbox, angle, cx=None, cy=None):
    """
    Rotate a bounding box by angle_deg degrees around (cx, cy).
    If cx/cy not provided, rotates around the bbox center.
    Returns the axis-aligned bounding box of the rotated corners.
    """
    if angle == 0:
        return bbox

    xmin, ymin, xmax, ymax = bbox

    if cx is None:
        cx = (xmin + xmax) / 2
    if cy is None:
        cy = (ymin + ymax) / 2

    corners = np.array(
        [
            [xmin, ymin],
            [xmax, ymin],
            [xmax, ymax],
            [xmin, ymax],
        ]
    )

    angle_rad = np.radians(angle)
    cos_a = np.cos(angle_rad)
    sin_a = np.sin(angle_rad)

    # Translate to origin, rotate, translate back
    corners -= [cx, cy]
    rotated = corners @ np.array([[cos_a, sin_a], [-sin_a, cos_a]])
    rotated += [cx, cy]

    return (
        rotated[:, 0].min(),
        rotated[:, 1].min(),
        rotated[:, 0].max(),
        rotated[:, 1].max(),
    )


def get_text_hw(text, font_size: int, font_weight: int = 400) -> tuple[float, float]:
    char_width = font_size * (0.8 if font_weight >= 500 else 0.6)
    width = len(text) * char_width
    height = font_size
    return height, width


def create_bbox(x, y, height, width) -> BBox:
    return [
        x,
        y,
        x + width,
        y + height,
    ]


class TextPlotterMixin:
    def __init__(self, *args, **kwargs):
        self._labels_rtree = rtree.index.Index()
        self._constellations_rtree = rtree.index.Index()
        self._stars_rtree = rtree.index.Index()
        self._markers_rtree = rtree.index.Index()

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
        # TODO
        return False
        return not self._clip_path_polygon.contains(box(*bbox))

    def _get_label_bbox(self, center, label, style) -> BBox:
        # self.fig.draw_without_rendering() # maybe dont need this line after all?
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

    def _add_label_to_rtree(self, label: str, bbox: BBox) -> None:
        """
        Adds a label to the R-Tree, which is a spatial index for all plotted labels and used for collision detection.

        If text debugging is enabled, then a white bounding box will be plotted around the label.

        Args:
            label: Annotation instance returned from matplotlib's annotate() function
            bbox: Tuple of integers representing bounding box (xmin, ymin, xmax, ymax) -- in display coordinates.
        """

        if self.debug_text:
            self._debug_bbox(bbox, color="white", width=1.5)

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

    def _text_point(
        self,
        ra: float,
        dec: float,
        text: str,
        collision_handler: CollisionHandler,
        **kwargs,
    ) -> None:
        # TODO
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
        style: LabelStyle,
        area,
        collision_handler: CollisionHandler,
    ) -> None:
        padding = 0
        max_distance = 2_000
        distance_step_size = 2
        attempts = 0
        height = None
        width = None
        bbox = None

        height, width = get_text_hw(
            text=text, font_size=style.font_size, font_weight=style.font_weight
        )

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
                        "symbol": "circle",
                        "color": "red",
                        "fill": "full",
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
                display_x, display_y = self.canvas._to_display(x, y)
                bbox = (
                    display_x,
                    display_y - height,
                    display_x + width,
                    display_y,
                )

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
                self.canvas.text(x, y, value=text, style=style, angle=0)
                self._add_label_to_rtree(text, bbox=bbox)
                if self.debug_text:
                    self._debug_bbox(bbox, color="red", width=1)
                return

            if is_final_attempt:
                return

    def _text_line(
        self,
        x,
        y,
        text: str,
        style: LabelStyle,
        num_labels: int = 1,
        collision_handler: CollisionHandler = None,
        min_spacing=None,
        curvature_threshold=0.8,
    ) -> None:
        """
        Plots text labels along a line:

        - Finds smoothest sections and tries those first
        - Falls back to evenly spaced labels (based on already plotted labels)

        Args:
            x, y: line data coordinates
            text: text to plot
            num_labels: Number of labels to plot
            collision_handler: Collision handler to use
            min_spacing: minimum spacing between labels (as fraction of line length). If None, uses 1/(n_labels+1)
            prefer_center: if True, place labels at center of smooth sections
            curvature_threshold: threshold for determining smooth sections

        """

        dx, dy = self.canvas._to_display(x, y)
        height, width = get_text_hw(
            text=text, font_size=style.font_size, font_weight=style.font_weight
        )

        # sort coords by display x value
        order = dx.argsort()
        dx = dx[order]
        dy = dy[order]
        display_xy = np.column_stack([dx, dy])

        num_positions = len(display_xy)

        if min_spacing is None:
            min_spacing = 1.0 / (num_labels + 1)


        def get_angle(x0, y0, x1, y1):
            # calculate angle in display coordinates
            dx_display = x1 - x0
            dy_display = y1 - y0
            angle = np.degrees(np.arctan2(dy_display, dx_display))

            # keep text upright
            if angle > 90:
                angle -= 180
            elif angle < -90:
                angle += 180

            return angle

        offset = num_positions // 20  # offset from start/end of line
        positions = [p for p in range(num_positions)]
        positions = positions[offset : -1 * offset]
        attempts = 0
        plotted_positions = set()

        while (
            len(plotted_positions) < num_labels
            and attempts < collision_handler.attempts
            and len(positions) > 0
        ):
            attempts += 1

            pos = next_best_position(
                plotted_positions, positions, num_labels, num_positions
            )
            if pos is None:
                return
            if pos in positions:
                positions.remove(pos)

            pos = max(0, min(pos, num_positions - 2))
            x0, y0 = display_xy[pos]
            x1, y1 = display_xy[pos + 1]
            y0 += height / 3  # center baseline hack
            y1 += height / 3
            angle = get_angle(
                x0,
                y0,
                x1,
                y1,
            )
            bbox = create_bbox(x0, y0, height=height, width=width)
            bbox = rotate_bbox(bbox, angle)

            # TODO : find better bbox (that's rotated with text)

            if bbox is None:
                continue

            is_open = self._is_open_space(
                bbox,
                padding=0,
                allow_clipped=collision_handler.allow_clipped,
                allow_constellation_collisions=collision_handler.allow_constellation_line_collisions,
                allow_marker_collisions=collision_handler.allow_marker_collisions,
                allow_label_collisions=collision_handler.allow_label_collisions,
            )
            is_final_attempt = attempts == collision_handler.attempts

            if is_open or (collision_handler.plot_on_fail and is_final_attempt):
                self.canvas._text_display(x0, y0, value=text, style=style, angle=angle)
                self._add_label_to_rtree(text, bbox=bbox)
                plotted_positions.add(pos)
                if self.debug_text and text:
                    self._debug_bbox(bbox, color="red", width=1)

            if is_final_attempt or len(plotted_positions) == num_labels:
                return

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
            collision_handler: An instance of [CollisionHandler][starplot.CollisionHandler] that describes what to do on collisions with other labels, markers, etc. If `None`, then the plot's `point_label_handler` will be used.
        """
        if not text:
            return

        style = style.model_copy()  # need a copy because we possibly mutate it below

        collision_handler = collision_handler or self.point_label_handler

        if style.offset_x == "auto":
            style.offset_x = 0

        if style.offset_y == "auto":
            style.offset_y = 0

        if kwargs.get("area"):
            self._text_area(
                ra,
                dec,
                text,
                style=style,
                area=kwargs.pop("area"),
                collision_handler=collision_handler,
            )
        else:
            self._text_point(
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

