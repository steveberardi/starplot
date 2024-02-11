from enum import Enum

from cartopy import crs as ccrs


class Projection(str, Enum):
    """Supported projections for MapPlots"""

    STEREO_NORTH = "stereo_north"
    """Good for objects near the north celestial pole, but distorts objects near the mid declinations"""

    STEREO_SOUTH = "stereo_south"
    """Good for objects near the south celestial pole, but distorts objects near the mid declinations"""

    MERCATOR = "mercator"
    """Good for declinations between -70 and 70, but distorts objects near the poles"""

    MOLLWEIDE = "mollweide"
    """Good for showing the entire celestial sphere in one plot"""

    MILLER = "miller"
    """Similar to Mercator: good for declinations between -70 and 70, but distorts objects near the poles"""

    ORTHOGRAPHIC = "orthographic"
    """Test"""

    STEREOGRAPHIC = "stereographic"
    """Test"""

    ZENITH = "zenith"
    """Test"""

    @staticmethod
    def crs(projection, center_lon=-180, **kwargs):
        projections = {
            Projection.STEREO_NORTH: ccrs.NorthPolarStereo,
            Projection.STEREO_SOUTH: ccrs.SouthPolarStereo,
            Projection.MERCATOR: ccrs.Mercator,
            Projection.MOLLWEIDE: ccrs.Mollweide,
            Projection.MILLER: ccrs.Miller,
            Projection.ORTHOGRAPHIC: ccrs.Orthographic,
            Projection.STEREOGRAPHIC: ccrs.Stereographic,
            Projection.ZENITH: ccrs.Stereographic
        }
        proj_class = projections.get(projection)
        if projection in [Projection.ORTHOGRAPHIC, Projection.STEREOGRAPHIC,Projection.ZENITH]:
            return proj_class(central_longitude=kwargs['lon'], central_latitude=kwargs['lat'])
        else:
            return proj_class(center_lon, **kwargs)