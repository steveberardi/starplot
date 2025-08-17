import numpy as np

# from matplotlib import patches, path
from matplotlib.colors import LinearSegmentedColormap

# from matplotlib.transforms import Affine2D
from starplot.profile import profile

# from starplot.optics import Optic


class GradientBackgroundMixin:
    """
    Mixin class to handle adding gradients to plots.

    Capable of handling a variety of projections and thus able to be used by
    HorizonPlot, OpticPlot, and MapPlot for vertical and radial gradients. However,
    some of the more obscure projections may throw errors if one attempts
    to plot a gradient with them.
    """

    @profile
    def apply_gradient_background(self, gradient_preset) -> None:
        """
        Adds a gradient background to the plot, beneath the GeoAxes.
        The background_color of the map must be set as a RGBA value with full
        transparency (e.g. #ffffff00) for this function to render the desired
        result.

        Args:
            gradient_preset: A list of tuples (e.g. [(0.0, '#000000'), (1.0, '#000080')])
                    where each tuple contains a position value [0-1] and a color
                    value to describe the range of colors in the gradient.
        """
        gradient_shape = self._find_gradient_shape()
        is_radial = (gradient_shape == "radial") or (gradient_shape == "mollweide")

        cmap = self._create_colormap(gradient_preset, reverse=(is_radial))
        background_ax = self._create_background_ax(gradient_shape)
        background_ax.set_axis_off()

        # Create arrays for gradient
        X, Y, gradient = self._create_gradient_arrays(gradient_shape)

        # Radial specific axes adjustment
        if gradient_shape == "radial":
            background_ax.set_ylim(Y.min(), Y.max() * 1.11)

        if gradient_shape == "camera":
            self._camera_optic_transform(background_ax)

        # Render gradient
        background_ax.pcolormesh(
            X,
            Y,
            gradient,
            cmap=cmap,
            shading="gouraud",
            rasterized=True,
            zorder=0,
        )

        # Set plot in self.ax's zorder to 1 so it appears above the gradient
        self.ax.zorder = 1

        # Event driven function so background_ax matches GeoAxes when plotted
        self.ax.figure.canvas.mpl_connect(
            "draw_event",
            lambda event: background_ax.set_position(self.ax.get_position()),
        )

    def _find_gradient_shape(self) -> str:
        """
        Default method to be overridden by plot classes.
        Determines what gradient shape should be used.
        Returns a string listing the gradient shape. At present this is "radial"
        or vertical. Defaults to "vertical".
        """
        return "vertical"

    def _create_colormap(self, gradient_preset, reverse=False):
        """
        Unzips color proportions and create colormap.

        Args:
            gradient_preset: A list of tuples containing the colors and their positions.
            reverse: bool for if the colormap should be in reverse order (for radial)

        Returns colormap or reversed colormap for radial plots
        """
        positions, colors = zip(*gradient_preset)
        cmap = LinearSegmentedColormap.from_list(
            "custom_gradient", list(zip(positions, colors)), N=750
        )
        return cmap.reversed() if reverse else cmap

    def _create_background_ax(self, gradient_shape):
        """
        Adds a set of axes to the plot to take the gradient image.

        Args:
            gradient_shape: string describing the gradient shape

        Returns an axes that is either polar or rectilinear depending on if the
        gradient is to be radial or vertical.
        """
        if gradient_shape == "radial":
            bbox = self.ax.get_position()
            projection_arg = "polar"
        else:
            bbox = self.ax.get_position()
            projection_arg = None

        return self.ax.figure.add_axes(bbox, zorder=0, projection=projection_arg)

    def _create_gradient_arrays(self, gradient_shape):
        """
        Creates arrays for the gradient placement and the gradient meshgrid.

        Args:
           gradient_shape: string describing the gradient shape

        Returns X, Y (array) for the coordinates of the corners of quadrilaterals
        of the pcolormesh, and gradient (array) for the gradient mesh data.
        """
        # Radial gradient
        if gradient_shape == "radial":
            rad = np.linspace(0, 1, 50)
            azm = np.linspace(0, 2 * np.pi, 100)
            # Y is the radius, X is theta
            Y, X = np.meshgrid(rad, azm)
            gradient = Y**2.0
            return X, Y, gradient

        # Elliptical gradient
        if gradient_shape == "mollweide":
            x = np.linspace(-2, 2, 1500)
            y = np.linspace(-1, 1, 1500)
            X, Y = np.meshgrid(x, y)
            mask = (X**2) / 4 + Y**2 <= 1
            R = np.sqrt((X / 2) ** 2 + Y**2)
            gradient = np.where(mask, R, np.nan)

        # Vertical Gradient
        else:
            x_array = np.linspace(0, 1, 2)
            y_array = np.linspace(0, 1, 750)
            X, Y = np.meshgrid(x_array, y_array)
            gradient = np.linspace(0, 1, 750).reshape(-1, 1)
            gradient = np.repeat(gradient, 2, axis=1)

        return X, Y, gradient

    def _camera_optic_transform(self, background_ax) -> None:
        """
        Transforms the background axes and adds patches to try and create a gradient
        affect for the camera optic.

        Args:
            background_ax: the axes where the gradient sits.

        Returns None
        """
        min_x, max_x = -0.11, 1.11
        min_y, max_y = -0.07, 1.07
        background_ax.set_xlim(min_x, max_x)
        background_ax.set_ylim(min_y, max_y)
        if self.optic.rotation == 0:
            return
        # TODO find better patch method/solution for rotated cameras.
        # outer_bound = path.Path([
        #                     (min_x, min_y),
        #                     (max_x, min_y),
        #                     (max_x, max_y),
        #                     (min_x, max_y),
        #                     (min_x, min_y)
        #                 ])
        # center_x, center_y = 0.5, 0.5
        # half_w, half_h   = 0.45, 0.3

        # rect_verts = np.array([
        #     [center_x-half_w, center_y-half_h],
        #     [center_x+half_w, center_y-half_h],
        #     [center_x+half_w, center_y+half_h],
        #     [center_x-half_w, center_y+half_h],
        #     [center_x-half_w, center_y-half_h]
        # ])
        # rotate_rect = Affine2D().rotate_deg_around(center_x, center_y, self.optic.rotation)
        # rect_path = rotate_rect.transform(rect_verts)
        # hole = rect_path[::-1]
        # vertices = np.vstack([outer_bound.vertices, hole])
        # codes = (
        #     [path.Path.MOVETO] + [path.Path.LINETO]*4 +
        #     [path.Path.MOVETO] + [path.Path.LINETO]*4
        # )
        # compound_path = path.Path(vertices, codes)
        # patch = patches.PathPatch(compound_path, facecolor='white')
        # background_ax.add_patch(patch)
