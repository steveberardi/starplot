from abc import ABC
from functools import cached_property

from cartopy import crs as ccrs
from pydantic import BaseModel


class CenterRA(BaseModel, ABC):
    center_ra: float = 0
    """Central right ascension"""


class CenterDEC(BaseModel, ABC):
    center_dec: float = 0
    """Central declination"""


class CenterRADEC(CenterRA, CenterDEC):
    pass


class ProjectionBase(BaseModel, ABC):
    threshold: int = 1000

    _ccrs = None

    class Config:
        arbitrary_types_allowed = True

    @cached_property
    def crs(self):
        kwargs = {}

        if hasattr(self, "center_ra"):
            kwargs["central_longitude"] = -1 * self.center_ra

        if hasattr(self, "center_dec"):
            kwargs["central_latitude"] = self.center_dec

        c = self._ccrs(**kwargs)
        c.threshold = self.threshold
        return c


class Miller(ProjectionBase, CenterRA):
    """Similar to Mercator: good for declinations between -70 and 70, but distorts objects near the poles"""

    _ccrs = ccrs.Miller


class Mercator(ProjectionBase, CenterRA):
    """Good for declinations between -70 and 70, but distorts objects near the poles"""

    _ccrs = ccrs.Mercator


class Mollweide(ProjectionBase, CenterRA):
    """Good for showing the entire celestial sphere in one plot"""

    _ccrs = ccrs.Mollweide


class Equidistant(ProjectionBase, CenterRADEC):
    """Shows accurate distances from the center position. Often used for planispheres."""

    _ccrs = ccrs.AzimuthalEquidistant


class StereoNorth(ProjectionBase, CenterRA):
    """Good for objects near the north celestial pole, but distorts objects near the mid declinations"""

    _ccrs = ccrs.NorthPolarStereo


class StereoSouth(ProjectionBase, CenterRA):
    """Good for objects near the south celestial pole, but distorts objects near the mid declinations"""

    _ccrs = ccrs.SouthPolarStereo


class Robinson(ProjectionBase, CenterRA):
    """Good for showing the entire celestial sphere in one plot"""

    _ccrs = ccrs.Robinson


class LambertAzEqArea(ProjectionBase, CenterRADEC):
    """Lambert Azimuthal Equal-Area projection - accurately shows area, but distorts angles."""

    _ccrs = ccrs.LambertAzimuthalEqualArea


class Orthographic(ProjectionBase, CenterRADEC):
    """Shows the celestial sphere as a 3D-looking globe. Objects near the edges will be distorted."""

    _ccrs = ccrs.Orthographic


class Stereographic(ProjectionBase, CenterRADEC):
    """Similar to the North/South Stereographic projection, but allows custom central declination"""

    _ccrs = ccrs.Stereographic
