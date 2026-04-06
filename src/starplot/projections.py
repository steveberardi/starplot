from abc import ABC
from functools import cached_property

import numpy as np
from cartopy import crs as ccrs
from pyproj import CRS, Proj, Transformer
from pydantic import BaseModel, Field

from starplot.constants import PROJ_R


def get_projection_bounds(projection: Proj, central_lon=0, n=100_000):
    min_lon = central_lon - 180
    max_lon = central_lon + 180

    lons = np.linspace(min_lon, max_lon, n)
    lats = np.linspace(-90, 90, n)

    top_x, top_y = projection.transform(lons, np.full(n, 90))
    bottom_x, bottom_y = projection.transform(lons, np.full(n, -90))
    left_x, left_y = projection.transform(np.full(n, min_lon), lats)
    right_x, right_y = projection.transform(np.full(n, max_lon), lats)

    all_x = np.concatenate([top_x, bottom_x, left_x, right_x])
    all_y = np.concatenate([top_y, bottom_y, left_y, right_y])

    valid = np.isfinite(all_x) & np.isfinite(all_y)

    return (
        all_x[valid].min(),
        all_y[valid].min(),
        all_x[valid].max(),
        all_y[valid].max(),
    )


def latlon_bounds_to_projection(
    lon_min: float,
    lat_min: float,
    lon_max: float,
    lat_max: float,
    target_crs: str | CRS,
    densify_edges: bool = True,
    densify_pts: int = 21,
) -> tuple[float, float, float, float]:
    """
    Convert a lat/lon bounding box to a target projection.

    Args:
        lat_min, lat_max: Latitude range in degrees
        lon_min, lon_max: Longitude range in degrees
        target_crs: Any pyproj-accepted CRS string (EPSG code, PROJ string, WKT)
        densify_edges: Sample points along each edge (important for curved projections)
        densify_pts: Number of points per edge when densifying

    Returns:
        Bounds in the target projection's native units
    """
    transformer = Transformer.from_crs("EPSG:4326", target_crs, always_xy=True)

    if densify_edges:
        # Sample along all 4 edges to catch curved projection boundaries
        top = [(lon, lat_max) for lon in np.linspace(lon_min, lon_max, densify_pts)]
        bottom = [(lon, lat_min) for lon in np.linspace(lon_min, lon_max, densify_pts)]
        left = [(lon_min, lat) for lat in np.linspace(lat_min, lat_max, densify_pts)]
        right = [(lon_max, lat) for lat in np.linspace(lat_min, lat_max, densify_pts)]
        corners = top + bottom + left + right
        lons, lats = zip(*corners)
    else:
        # Just the 4 corners
        lons = [lon_min, lon_max, lon_min, lon_max]
        lats = [lat_min, lat_min, lat_max, lat_max]

    xs, ys = transformer.transform(lons, lats)

    # Filter out inf values (points that don't project)
    valid = [(x, y) for x, y in zip(xs, ys) if abs(x) < 1e15 and abs(y) < 1e15]
    if not valid:
        raise ValueError("No valid projected points — check your CRS and bounds")

    xs_v, ys_v = zip(*valid)
    return min(xs_v), min(ys_v), max(xs_v), max(ys_v)


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

    proj_def_base: str = None
    global_only: bool = False

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

    @property
    def edge_x(self) -> float | None:
        return None

    @property
    def global_bounds(self):
        return latlon_bounds_to_projection(
            -180,
            -90,
            180,
            90,
            target_crs=CRS.from_proj4(self.proj_def_base),
        )


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

    proj_def_base: str = f"+proj=mill +R={PROJ_R} +units=m"

    @property
    def _crs(self):
        return CRS.from_proj4(
            f"+proj=mill +lat_0=0 +lon_0={360 - self.center_ra} +x_0=0 +y_0=0 +R={PROJ_R} +units=m"
        )

    @property
    def edge_x(self) -> float | None:
        if self.center_ra < 180:
            return self.center_ra + 180

        return self.center_ra - 180


class Mercator(ProjectionBase, CenterRA):
    """Good for declinations between -70 and 70, but distorts objects near the poles"""

    _ccrs = ccrs.Mercator


class PlateCarree(ProjectionBase, CenterRA):
    """An equirectangular projection"""

    _ccrs = ccrs.PlateCarree


class ObliqueMercator(ProjectionBase, CenterRADEC, Azimuth):
    """Oblique Mercator projection"""

    _ccrs = ccrs.ObliqueMercator


class Mollweide(ProjectionBase, CenterRA):
    """Good for showing the entire celestial sphere in one plot"""

    _ccrs = ccrs.Mollweide

    proj_def_base: str = f"+proj=moll +R={PROJ_R} +units=m"
    global_only: bool = True

    @property
    def _crs(self):
        return CRS.from_proj4(
            f"+proj=moll +lon_0={360 - self.center_ra} +R={PROJ_R} +units=m"
        )


class Equidistant(ProjectionBase, CenterRADEC):
    """Shows accurate distances from the center position. Often used for planispheres."""

    _ccrs = ccrs.AzimuthalEquidistant

    @property
    def _crs(self):
        return CRS.from_proj4(
            f"+proj=aeqd +lat_0={self.center_dec} +lon_0={360 - self.center_ra} +R={PROJ_R} +units=m"
        )


class EquidistantOptic(ProjectionBase, CenterRADEC):
    """Shows accurate distances from the center position. Often used for planispheres."""

    _ccrs = ccrs.AzimuthalEquidistant

    @property
    def _crs(self):
        return CRS.from_proj4(
            f"+proj=aeqd +lat_0={self.center_dec} +lon_0={self.center_ra} +R={PROJ_R} +units=m"
        )


class StereoNorth(ProjectionBase, CenterRA):
    """Good for objects near the north celestial pole, but distorts objects near the mid declinations"""

    _ccrs = ccrs.NorthPolarStereo

    @property
    def _crs(self):
        return CRS.from_proj4(
            f"+proj=stere +lat_0=90 +lon_0={360 - self.center_ra}  +R={PROJ_R} +units=m"
        )


class StereoSouth(ProjectionBase, CenterRA):
    """Good for objects near the south celestial pole, but distorts objects near the mid declinations"""

    _ccrs = ccrs.SouthPolarStereo

    @property
    def _crs(self):
        return CRS.from_proj4(
            f"+proj=stere +lat_0=-90 +lon_0={360 - self.center_ra}  +R={PROJ_R} +units=m"
        )


class Robinson(ProjectionBase, CenterRA):
    """Good for showing the entire celestial sphere in one plot"""

    _ccrs = ccrs.Robinson

    global_only: bool = True


class LambertAzEqArea(ProjectionBase, CenterRADEC):
    """Lambert Azimuthal Equal-Area projection - accurately shows area, but distorts angles."""

    _ccrs = ccrs.LambertAzimuthalEqualArea


class Orthographic(ProjectionBase, CenterRADEC):
    """Shows the celestial sphere as a 3D-looking globe. Objects near the edges will be distorted."""

    _ccrs = ccrs.Orthographic

    proj_def_base: str = f"+proj=ortho +R={PROJ_R} +units=m"
    global_only: bool = True

    @property
    def _crs(self):
        return CRS.from_proj4(
            f"+proj=ortho +lat_0={self.center_dec} +lon_0={360 - self.center_ra}  +R={PROJ_R} +units=m"
        )


class Stereographic(ProjectionBase, CenterRADEC):
    """Similar to the North/South Stereographic projection, but allows custom central declination"""

    _ccrs = ccrs.Stereographic
