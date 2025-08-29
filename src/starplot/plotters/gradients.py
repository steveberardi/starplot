import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from starplot.profile import profile
from starplot.styles import GradientDirection


class GradientBackgroundMixin:
    """
    Mixin class to handle adding gradients to plots.

    Handles a variety of projections and can be inherited by HorizonPlot, OpticPlot,
    and MapPlot for vertical, radial, and mollweide gradients. However, some more
    obscure projections may throw errors if attempting to plot a gradient with them.
    """

    @profile
    def _plot_gradient_background(
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
        direction = self._gradient_direction
        reverse = True if direction == GradientDirection.RADIAL else False
        cmap = self._create_colormap(gradient_preset, reverse=reverse)
        background_ax = self._create_background_ax()
        background_ax.set_axis_off()
        self._background_ax = background_ax

        X, Y, gradient = self._create_gradient_arrays()

        # Radial specific axes adjustments
        if self._gradient_direction == GradientDirection.RADIAL:
            background_ax.set_ylim(Y.min(), Y.max() * 1.06)

        # if getattr(self, "optic", None):
        #     self._camera_optic_transform(background_ax)
        # Camera specific axes adjustments
        # if gradient_shape == "camera":
        #     self._camera_optic_transform(background_ax)

        # Render gradient
        background_ax.pcolormesh(
            X,
            Y,
            gradient,
            cmap=cmap,
            shading="gouraud",
            rasterized=True,
            zorder=0,
            clip_path=self._background_clip_path,
        )

        # Set plot in self.ax's zorder to 1 so it appears above the gradient
        self.ax.zorder = 1

        # Event driven function so background_ax matches GeoAxes when plotted
        self.ax.figure.canvas.mpl_connect(
            "draw_event",
            lambda event: background_ax.set_position(self.ax.get_position()),
        )

    def _create_colormap(
        self, gradient_preset: list[tuple[float, str]], reverse: bool = False
    ) -> LinearSegmentedColormap:
        """Creates a matplotlib colormap from a gradient preset."""
        positions, colors = zip(*gradient_preset)

        if self._gradient_direction == GradientDirection.RADIAL:
            positions = [p / 2 for p in positions]
            positions[-1] = 1

        from pydantic.color import Color

        colors = [Color(c).as_hex() for c in colors]

        cmap = LinearSegmentedColormap.from_list(
            "custom_gradient", list(zip(positions, colors)), N=750
        )
        return cmap.reversed() if reverse else cmap

    def _create_background_ax(self):
        """Adds a set of axes to take the gradient image."""
        bbox = self.ax.get_position()
        projection = None

        if self._gradient_direction == GradientDirection.RADIAL:
            projection = "polar"
        elif self._gradient_direction == GradientDirection.MOLLWEIDE:
            projection = "mollweide"

        return self.ax.figure.add_axes(bbox, zorder=0, projection=projection)

    def _create_gradient_arrays(self):
        """Creates arrays for the gradient placement and the gradient meshgrid."""
        # Radial gradient
        if self._gradient_direction == GradientDirection.RADIAL:
            rad = np.linspace(0, 1, 50)
            azm = np.linspace(0, 2 * np.pi, 100)
            Y, X = np.meshgrid(rad, azm)
            gradient = Y**2.0
            return X, Y, gradient

        # Mollweide gradient
        if self._gradient_direction == GradientDirection.MOLLWEIDE:
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
