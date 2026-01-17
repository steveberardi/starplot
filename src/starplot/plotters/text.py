from dataclasses import dataclass
from random import randrange

import numpy as np
import rtree
from shapely import Polygon, Point

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
    allow_clipped: bool = False
    allow_label_collisions: bool = False
    allow_marker_collisions: bool = False
    allow_constellation_line_collisions: bool = False

    plot_on_fail: bool = False

    attempts: int = 100

    anchor_fallbacks: list[AnchorPointEnum] = None

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

    def _get_label_bbox(self, label) -> BBox:
        extent = label.get_window_extent(renderer=self.fig.canvas.get_renderer())
        return (extent.x0, extent.y0, extent.x1, extent.y1)

    def _maybe_remove_label(
        self,
        label,
        remove_on_collision=True,
        remove_on_clipped=True,
        remove_on_constellation_collision=True,
    ) -> bool:
        """Returns true if the label is removed, else false"""
        extent = label.get_window_extent(renderer=self.fig.canvas.get_renderer())
        bbox = self._get_label_bbox(label)
        points = [(extent.x0, extent.y0), (extent.x1, extent.y1)]

        if any([np.isnan(c) for c in bbox]):
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
        collision_handler: CollisionHandler,
        hide_on_collision: bool,
        force: bool = False,
        clip_on: bool = True,
        **kwargs,
    ):
        if not text:
            return None

        x, y = self._prepare_coords(ra, dec)

        if StarplotSettings.svg_text_type == SvgTextType.PATH:
            kwargs["path_effects"] = kwargs.get("path_effects", [self.text_border])

        remove_on_constellation_collision = kwargs.pop(
            "remove_on_constellation_collision", True
        )

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
        hide_on_collision: bool,
        collision_handler: CollisionHandler,
        clip_on: bool = True,
        settings: dict = None,
        **kwargs,
    ) -> None:
        kwargs["va"] = "center"
        kwargs["ha"] = "center"

        if StarplotSettings.svg_text_type == SvgTextType.PATH:
            kwargs["path_effects"] = kwargs.get("path_effects", [self.text_border])

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
        collision_handler: CollisionHandler = CollisionHandler(),
        **kwargs,
    ):
        """
        Plots text

        Args:
            text: Text to plot
            ra: Right ascension of text (0...360)
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
                collision_handler=collision_handler,
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
                collision_handler=collision_handler,
                xycoords="data",
                xytext=(style.offset_x * self.scale, style.offset_y * self.scale),
                textcoords="offset points",
                **kwargs,
            )
