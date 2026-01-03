import random

import numpy as np

from matplotlib import patches
from shapely import LineString, Polygon, affinity, ops

from starplot.geometry import circle
from starplot.profile import profile
from starplot.coordinates import CoordinateSystem
from starplot.styles import ArrowStyle
from starplot.styles.helpers import use_style
from starplot.utils import points_on_line


class ArrowPlotterMixin:
    def _to_axes(self, points):
        ax_points = []

        for ra, dec in points:
            x, y = self._proj.transform_point(ra, dec, self._crs)
            data_to_axes = self.ax.transData + self.ax.transAxes.inverted()
            x_axes, y_axes = data_to_axes.transform((x, y))
            ax_points.append([x_axes, y_axes])
        return ax_points

    def _to_display(self, points):
        display_points = []

        for ra, dec in points:
            if self._coordinate_system == CoordinateSystem.RA_DEC:
                ra *= -1

            data_x, data_y = self._proj.transform_point(ra, dec, self._geodetic)
            if np.isnan(data_x) or np.isnan(data_y):
                continue

            display_x, display_y = self.ax.transData.transform((data_x, data_y))
            display_points.append((display_x, display_y))

        return display_points

    @profile
    @use_style(ArrowStyle, "arrow")
    def arrow(
        self,
        origin: tuple[float, float] = None,
        target: tuple[float, float] = None,
        style: ArrowStyle = None,
        scale: float = 0.99,
        length: float = 5,
        max_attempts: int = 100,
    ):
        """
        Plots an arrow from one point to another.

        Args:
            origin: Starting point (ra, dec)
            target: Target of the arrow (ra, dec)
            style: Style of the arrow
            scale: Scaling factor for the arrow, to make it offset from the origin/target
            length: If you only specify a target, then this will be the length of the arrow (in degrees). This value is ignored if you're plotting an arrow from one point to another.
            max_attempts: If you only specify a target, then this will be the max number of attempts for plotting the arrow without colliding with labels. Arrow will be plotted on the final attempt.

        """

        def create_arrow(p0, p1):
            ax_coords = self._to_axes([origin, target])
            x, y = ax_coords[0]
            target_x, target_y = ax_coords[1]

            # angle to rotate head
            angle_radians = np.atan2(target_y - y, target_x - x)
            angle_degrees = np.degrees(angle_radians)

            line_x = [
                (1 - scale) * ax_coords[1][0] + scale * ax_coords[0][0],
                (1 - scale) * ax_coords[0][0] + scale * ax_coords[1][0],
            ]
            line_y = [
                (1 - scale) * ax_coords[1][1] + scale * ax_coords[0][1],
                (1 - scale) * ax_coords[0][1] + scale * ax_coords[1][1],
            ]

            arrow_x = line_x[-1]
            arrow_y = line_y[-1]

            body_width = style.body_width / self.resolution * 0.5
            head_width = style.head_width / self.resolution * 0.5
            head_height = style.head_height / self.resolution * 0.5

            arrow_line = LineString(list(zip(line_x, line_y)))
            arrow_body = arrow_line.buffer(body_width, **style.shapely_kwargs())

            arrow_head = Polygon(
                [
                    (arrow_x, arrow_y),
                    (arrow_x + head_width, arrow_y - head_height),
                    (arrow_x - head_width, arrow_y - head_height),
                    (arrow_x, arrow_y),
                ]
            )

            arrow_head = affinity.rotate(
                arrow_head,
                angle_degrees + 270,
                origin=(arrow_x, arrow_y),
            )

            result = ops.split(arrow_line, arrow_head)
            arrow_body = result.geoms[0].buffer(body_width, **style.shapely_kwargs())
            return arrow_body.union(arrow_head.buffer(0.0001, **style.shapely_kwargs()))

        if origin and target:
            origin = self._prepare_coords(*origin)
            target = self._prepare_coords(*target)
            arrow_polygon = create_arrow(origin, target)

        elif target:
            # we only need to prepare the target coords because the origin will be
            # based on the circle around the prepared target coords (so the origin will be automatically in the expected coord system)
            target = self._prepare_coords(*target)
            arrow_polygon = None
            attempts = 0
            padding = 8
            polygon = circle(
                center=target,
                diameter_degrees=length * 2,
                num_pts=200,
            )

            origins = list(zip(*polygon.exterior.coords.xy))

            while arrow_polygon is None and attempts < max_attempts:
                attempts += 1
                origin = random.choice(origins)
                display_points = self._to_display([origin, target])

                if len(display_points) < 2:
                    continue

                points_arrow = points_on_line(display_points[0], display_points[1], 25)

                # check if arrow body collides with any labels
                collides_with_label = False
                for x, y in points_arrow:
                    bbox = (
                        x - padding,
                        y - padding,
                        x + padding,
                        y + padding,
                    )
                    if self._is_label_collision(bbox):
                        collides_with_label = True
                        break

                # if arrow body does not collide with labels, we can create polygon and exit loop
                if not collides_with_label or attempts == max_attempts:
                    arrow_polygon = create_arrow(origin, target)

        else:
            raise ValueError(
                "To plot an arrow you must specify a target or a target and origin."
            )

        patch = patches.Polygon(
            list(zip(*arrow_polygon.exterior.coords.xy)),
            **style.matplot_kwargs(self.scale),
            transform=self.ax.transAxes,
        )
        self.ax.add_patch(patch)
        # Need to set clip path AFTER adding patch
        patch.set_clip_on(True)
        patch.set_clip_path(self._background_clip_path)
