from abc import ABC
from functools import cached_property

from cartopy import crs as ccrs
from pydantic import BaseModel, Field


class CenterRA(BaseModel, ABC):
    center_ra: float = Field(default=180, ge=0, le=360)
    """Central right ascension"""


class CenterDEC(BaseModel, ABC):
    center_dec: float = Field(default=0, ge=-90, le=90)
    """Central declination"""


class CenterRADEC(CenterRA, CenterDEC):
    pass


class Azimuth(BaseModel, ABC):
    azimuth: float = Field(default=0, ge=0, le=360)
    """Direction of central line of the projection"""


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

        if hasattr(self, "azimuth"):
            kwargs["azimuth"] = self.azimuth

        c = self._ccrs(**kwargs)
        c.threshold = self.threshold
        return c


class AutoProjection:
    """
    Automatically selects a projection based on the RA/DEC extent you specify when creating the map plot.

    This uses a pretty simple method:

    1. If the extent is the full celestial sphere (RA is 0 to 360 and DEC is -90 to 90), then it'll use Mollweide

    2. If the max declination is greater than 75 and the min is greater than or equal to 0, then it'll use a Stereographic North projection

    3. If the max declination is less than or equal to 0 and the min is less than -75, then it'll use a Stereographic South projection

    4. If the extent doesn't match any of the above, then it'll use a Miller projection

    In all cases, it sets the central RA to the midpoint of the RA extent.

    Unlike the other projection options, this class does not expose any public parameters (e.g. center RA/DEC), since everything is determined automatically.

    To use this automatic projection:

    ```python

    from starplot import MapPlot, AutoProjection

    p = MapPlot(
        projection=AutoProjection(),
        ra_min=4 * 15,
        ra_max=6 * 15,
        dec_min=0,
        dec_max=20,
    )
    ```
    """

    def _is_global(
        self, ra_min: float, ra_max: float, dec_min: float, dec_max: float
    ) -> bool:
        return ra_min == 0 and ra_max == 360 and dec_min == -90 and dec_max == 90

    def crs(self, ra_min: float, ra_max: float, dec_min: float, dec_max: float):
        central_longitude = -1 * (ra_min + ra_max) / 2

        if self._is_global(ra_min, ra_max, dec_min, dec_max):
            c = ccrs.Mollweide(central_longitude=central_longitude)

        elif dec_max < 75 and dec_min > -75:
            c = ccrs.Miller(central_longitude=central_longitude)

        elif dec_max > 75 and dec_min >= 0:
            c = ccrs.NorthPolarStereo(central_longitude=central_longitude)

        elif dec_max <= 0 and dec_min < -75:
            c = ccrs.SouthPolarStereo(central_longitude=central_longitude)

        else:
            c = ccrs.Miller(central_longitude=central_longitude)

        c.threshold = 1_000

        return c


class Miller(ProjectionBase, CenterRA):
    """Similar to Mercator: good for declinations between -70 and 70, but distorts objects near the poles"""

    _ccrs = ccrs.Miller


class Mercator(ProjectionBase, CenterRA):
    """Good for declinations between -70 and 70, but distorts objects near the poles"""

    _ccrs = ccrs.Mercator


class ObliqueMercator(ProjectionBase, CenterRADEC, Azimuth):
    """Oblique Mercator projection"""

    _ccrs = ccrs.ObliqueMercator


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
