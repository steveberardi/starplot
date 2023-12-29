import math

from abc import ABC, abstractmethod

import pyproj

from matplotlib import patches

from starplot.utils import in_circle


class Optic(ABC):
    """Abstract class for defining Optics."""

    def __init__(self) -> None:
        pass

    def __str__(self):
        return "Optic"

    @property
    @abstractmethod
    def xlim(self):
        pass

    @property
    @abstractmethod
    def ylim(self):
        pass

    @property
    @abstractmethod
    def label(self):
        return "Abstract Optic"

    @abstractmethod
    def patch(self, center_x, center_y) -> patches.Patch:
        pass

    def transform(self, axis) -> None:
        pass

    @abstractmethod
    def in_bounds(self, x, y, scale: float = 1) -> bool:
        pass

    def _compute_radius(self, radius_degrees: float, x: float = 0, y: float = 0):
        geod = pyproj.Geod("+a=6378137 +f=0.0", sphere=True)
        _, _, distance = geod.inv(x, y, x + radius_degrees, y)
        return distance


class Scope(Optic):
    """Creates a new generic Scope optic.

    Use this class to create custom scope optics or use it as a generic optic that does NOT apply any transforms to the view.

    See subclasses of this optic for more specific use cases:

    - [`Refractor`][starplot.optics.Refractor] - automatically inverts the view (i.e. assumes a star diagonal is used)

    - [`Reflector`][starplot.optics.Reflector] - automatically rotates the view so it's upside-down

    Args:
        focal_length: Focal length (mm) of the telescope
        eyepiece_focal_length: Focal length (mm) of the eyepiece
        eyepiece_fov: Field of view (degrees) of the eyepiece

    Returns:
        Scope: A new instance of a Scope optic
    """

    def __init__(
        self, focal_length: float, eyepiece_focal_length: float, eyepiece_fov: float
    ) -> None:
        self.focal_length = focal_length
        self.eyepiece_focal_length = eyepiece_focal_length
        self.eyepiece_fov = eyepiece_fov
        self.magnification = self.focal_length / self.eyepiece_focal_length
        self.true_fov = self.eyepiece_fov / self.magnification
        self.radius = self._compute_radius(self.true_fov / 2)

    def __str__(self):
        return f"{self.focal_length}mm w/ {self.eyepiece_focal_length}mm ({self.magnification:.0f}x) @  {self.eyepiece_fov:.0f}\N{DEGREE SIGN} = {self.true_fov:.2f}\N{DEGREE SIGN} TFOV"

    @property
    def xlim(self):
        return self.radius

    @property
    def ylim(self):
        return self.radius

    @property
    def label(self):
        return "Scope"

    def patch(self, center_x, center_y, **kwargs):
        padding = kwargs.pop("padding", 0)
        return patches.Circle(
            (center_x, center_y),
            radius=self.radius + padding,
            **kwargs,
        )

    def in_bounds(self, x, y, scale: float = 1) -> bool:
        return in_circle(x, y, 0, 0, self.radius * scale)


class Refractor(Scope):
    """Creates a new Refractor Telescope optic

    Warning:
        This optic assumes a star diagonal is used, so it applies a transform that inverts the image.

        If you don't want this transform applied, then use the generic [`Scope`][starplot.optics.Scope] optic instead.

    Args:
        focal_length: Focal length (mm) of the telescope
        eyepiece_focal_length: Focal length (mm) of the eyepiece
        eyepiece_fov: Field of view (degrees) of the eyepiece

    Returns:
        Refractor: A new instance of a Refractor optic

    """

    @property
    def label(self):
        return "Refractor"

    def transform(self, axis) -> None:
        axis.invert_xaxis()


class Reflector(Scope):
    """Creates a new Reflector Telescope optic

    Warning:
        This optic applies a transform that produces an "upside-down" image.

        If you don't want this transform applied, then use the generic [`Scope`][starplot.optics.Scope] optic instead.

    Args:
        focal_length: Focal length (mm) of the telescope
        eyepiece_focal_length: Focal length (mm) of the eyepiece
        eyepiece_fov: Field of view (degrees) of the eyepiece

    Returns:
        Reflector: A new instance of a Reflector optic

    """

    @property
    def label(self):
        return "Reflector"

    def transform(self, axis) -> None:
        axis.invert_yaxis()


class Binoculars(Optic):
    """Creates a new Binoculars optic

    Args:
        magnification: Magnification of the binoculars
        fov: Apparent field of view (FOV) of the binoculars in degrees. This isn't always easy to find for binoculars, so if you can't find it in your binocular's specs, then try using `60`.

    Returns:
        Binoculars: A new instance of a Binoculars optic

    """

    def __init__(self, magnification: float, fov: float) -> None:
        self.magnification = magnification
        self.apparent_fov = fov
        self.true_fov = self.apparent_fov / self.magnification
        self.radius = self._compute_radius(self.true_fov / 2)

    def __str__(self):
        return f"{self.magnification}x @ {self.apparent_fov}\N{DEGREE SIGN} = {self.true_fov}\N{DEGREE SIGN}"

    @property
    def xlim(self):
        return self.radius

    @property
    def ylim(self):
        return self.radius

    @property
    def label(self):
        return "Binoculars"

    def patch(self, center_x, center_y, **kwargs):
        padding = kwargs.pop("padding", 0)
        return patches.Circle(
            (center_x, center_y),
            radius=self.radius + padding,
            **kwargs,
        )

    def in_bounds(self, x, y, scale: float = 1) -> bool:
        return in_circle(x, y, 0, 0, self.radius * scale)


class Camera(Optic):
    """Creates a new Camera optic

    Note:
        Field of view for each dimension is calculated using the following formula:

        ```
        TFOV = 2 * arctan( d / (2 * f) )
        ```

        _Where_:

        d = sensor size (height or width)

        f = focal length of lens

    Args:
        sensor_height: Height of camera sensor (mm)
        sensor_width: Width of camera sensor (mm)
        lens_focal_length: Focal length of camera lens (mm)

    Returns:
        Camera: A new instance of a Camera optic

    """

    def __init__(
        self, sensor_height: float, sensor_width: float, lens_focal_length: float
    ) -> None:
        self.sensor_height = sensor_height
        self.sensor_width = sensor_width
        self.lens_focal_length = lens_focal_length

        self.true_fov_x = 2 * math.degrees(
            math.atan(self.sensor_width / (2 * self.lens_focal_length))
        )
        self.true_fov_y = 2 * math.degrees(
            math.atan(self.sensor_height / (2 * self.lens_focal_length))
        )
        self.true_fov = max(self.true_fov_x, self.true_fov_y)

        self.radius_x = self._compute_radius(self.true_fov_x / 2)
        self.radius_y = self._compute_radius(self.true_fov_y / 2)

    def __str__(self):
        return f"{self.sensor_width}x{self.sensor_height} w/ {self.lens_focal_length}mm lens = {self.true_fov_x:.2f}\N{DEGREE SIGN} x {self.true_fov_y:.2f}\N{DEGREE SIGN}"

    @property
    def xlim(self):
        return self.radius_x

    @property
    def ylim(self):
        return self.radius_y

    @property
    def label(self):
        return "Camera"

    def patch(self, center_x, center_y, **kwargs):
        padding = kwargs.pop("padding", 0)
        x = center_x - self.radius_x - padding
        y = center_y - self.radius_y - padding
        return patches.Rectangle(
            (x, y),
            self.radius_x * 2 + padding,
            self.radius_y * 2 + padding,
            **kwargs,
        )

    def in_bounds(self, x, y, scale: float = 1) -> bool:
        in_bounds_x = x < self.radius_x * scale and x > 1 - self.radius_x * scale
        in_bounds_y = y < self.radius_y * scale and y > 1 - self.radius_y * scale
        return in_bounds_x and in_bounds_y
