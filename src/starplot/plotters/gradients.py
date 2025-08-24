import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from starplot.profile import profile


class GradientBackgroundMixin:
    """
    Mixin class to handle adding gradients to plots.

    Handles a variety of projections and can be inherited by HorizonPlot, OpticPlot,
    and MapPlot for vertical, radial, and mollweide gradients. However, some more
    obscure projections may throw errors if attempting to plot a gradient with them.
    """

    @profile
    def apply_gradient_background(
        self, gradient_preset: list[tuple[float, str]]
    ) -> None:
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
        is_radial = gradient_shape == "radial"

        cmap = self._create_colormap(gradient_preset, reverse=is_radial)
        background_ax = self._create_background_ax(gradient_shape)
        background_ax.set_axis_off()

        X, Y, gradient = self._create_gradient_arrays(gradient_shape)

        # Radial specific axes adjustments
        if gradient_shape == "radial":
            background_ax.set_ylim(Y.min(), Y.max() * 1.11)

        # Camera specific axes adjustments
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
        Returns a string of the gradient shape, defaulting to "vertical".
        """
        return "vertical"

    def _create_colormap(
        self, gradient_preset: list[tuple[float, str]], reverse: bool = False
    ) -> LinearSegmentedColormap:
        """Creates a matplotlib colormap from a gradient preset."""
        positions, colors = zip(*gradient_preset)
        cmap = LinearSegmentedColormap.from_list(
            "custom_gradient", list(zip(positions, colors)), N=750
        )
        return cmap.reversed() if reverse else cmap

    def _create_background_ax(self, gradient_shape: str):
        """Adds a set of axes to take the gradient image."""
        bbox = self.ax.get_position()
        projection_arg = None
        if gradient_shape in ("radial", "mollweide"):
            projection_arg = "polar" if gradient_shape == "radial" else "mollweide"
        return self.ax.figure.add_axes(bbox, zorder=0, projection=projection_arg)

    def _create_gradient_arrays(self, gradient_shape: str):
        """Creates arrays for the gradient placement and the gradient meshgrid."""
        # Radial gradient
        if gradient_shape == "radial":
            rad = np.linspace(0, 1, 50)
            azm = np.linspace(0, 2 * np.pi, 100)
            Y, X = np.meshgrid(rad, azm)
            gradient = Y**2.0
            return X, Y, gradient

        # Mollweide gradient
        if gradient_shape == "mollweide":
            return self._create_mollweide_gradient()

        # Default Vertical Gradient
        x_array = np.linspace(0, 1, 2)
        y_array = np.linspace(0, 1, 750)
        X, Y = np.meshgrid(x_array, y_array)
        gradient = np.linspace(0, 1, 750).reshape(-1, 1)
        gradient = np.repeat(gradient, 2, axis=1)
        return X, Y, gradient

    def _create_mollweide_gradient(self):
        """Generate meshgrid and gradient for a mollweide projection."""
        x = np.linspace(-np.pi, np.pi, 250)
        y = np.linspace(-np.pi / 2, np.pi / 2, 250)
        X, Y = np.meshgrid(x, y)
        # Rotation matrix (ICRS → Galactic)
        R = np.array(
            [
                [-0.0548755604162154, -0.8734370902348850, -0.4838350155487132],
                [0.4941094278755837, -0.4448296299600112, 0.7469822444972189],
                [-0.8676661490190047, -0.1980763734312015, 0.4559837761750669],
            ]
        )
        # Equatorial unit vectors
        cos_y = np.cos(Y)
        eq = np.stack(
            [cos_y * np.cos(X), cos_y * np.sin(X) * -1, np.sin(Y) * -1], axis=-1
        )
        # Rotate into Galactic coords
        gal = eq @ R.T
        # Gradient follows galactic latitude
        gradient = np.arcsin(gal[..., 2])
        return X, Y, gradient

    def _camera_optic_transform(self, background_ax) -> None:
        """Apply camera-specific axes transformations for the gradient."""
        background_ax.set_xlim(-0.11, 1.11)
        background_ax.set_ylim(-0.07, 1.07)
        if self.optic.rotation == 0:
            return
