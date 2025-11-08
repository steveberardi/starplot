import numpy as np

from starplot.geometry import circle
from starplot.profile import profile


class ArrowPlotterMixin:
    def _to_axes(self, points):
        ax_points = []

        for ra, dec in points:
            x, y = self._proj.transform_point(ra, dec, self._crs)
            data_to_axes = self.ax.transData + self.ax.transAxes.inverted()
            x_axes, y_axes = data_to_axes.transform((x, y))
            ax_points.append([x_axes, y_axes])
        return ax_points

    @profile
    def arrow(
        self,
        origin: tuple[float, float] = None,
        target: tuple[float, float] = None,
        scale: float = 0.9,
        length: float = 1,
    ):
        """
        Plots an arrow from one point to another.

        Args:
            origin: Starting point (ra, dec)
            target: Target of the arrow (ra, dec)
            scale: Scaling factor for the arrow, to make it offset from the origin/target
            length: If you only specify a target, then this will be the length of the arrow (in degrees). This value is ignored if you're plotting an arrow from one point to another.
            style: Style of the arrow

            TODO : add style kwarg

            Draw as polygon instead
        """
        # self._text(x, y, labels[i], **text_kwargs)
        # self.ax.annotate("", xytext=(0, 0), xy=(0.5, 0.5),
        #     )
        # # y = mx + b
        # def _slope(x1, y1, x2, y2):
        #     return (y2-y1)/(x2-x1)
        # slope = _slope(x, y, target_x, target_y)
        # b = y - slope * x

        """
        Do this in display coords
        
        1. Create LineString
        2. Segmentize
        3. Buffer
        4. Create arrow head (triangle)
        """

        if origin and target:
            # TODO : prepare coords
            ax_coords = self._to_axes([origin, target])
            x, y = ax_coords[0]
            target_x, target_y = ax_coords[1]

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

            # plot line
            self.ax.plot(
                line_x,
                line_y,
                clip_on=True,
                clip_path=self._background_clip_path,
                color="red",
                linewidth=5,
                transform=self.ax.transAxes,
            )

            arrow_x = line_x[-1]
            arrow_y = line_y[-1]

            # plot arrowhead
            self.ax.plot(
                arrow_x,
                arrow_y,
                marker=(3, 0, angle_degrees + 270),
                markersize=30,
                color="red",
                linestyle="None",
                transform=self.ax.transAxes,
            )
        elif target:
            polygon = circle(
                center=target,
                diameter_degrees=length,
                num_pts=200,
            )

            list(zip(*polygon.exterior.coords.xy))

            """
            TODO :
            add support for target only:
            length param (in degrees)
            1. create circle
            2. try random points on circle
            3. generate points on line from origin to target
            4. if points collide with label, try another random point
            5. stop when no collisions with labels
            """

        else:
            raise ValueError(
                "To plot an arrow you must specify a target or a target and origin."
            )

        # Convert to display coordinates
        # display_x, display_y = ax.transAxes.transform((axes_x, axes_y))

        # points = geod.ellipse(
        #     center=(),
        #     height_degrees,
        #     width_degrees,
        #     num_pts=200,
        # )

        # self.ax.arrow(
        #     x,
        #     y,
        #     target_x - x,
        #     target_y - y,
        #     color="red",
        #     head_length=1,
        #     head_width=1,
        #     transform=self.ax.transAxes,
        # )

        # ra, dec = to
        # x, y = self._prepare_coords(ra, dec)

        # self.ax.annotate(
        #     "",
        #     xy=(x, y),
        #     xytext=(0, 0),
        #     arrowprops=dict(
        #         # headlength=10,
        #         # headwidth=16,
        #         color="red",
        #         # shrink=0.9,
        #         mutation_scale=5,
        #         arrowstyle="-|>, head_length=10, head_width=5",
        #     ),
        #     **self._plot_kwargs(),
        # )
