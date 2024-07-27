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
    """
    Shows the celestial sphere as a 3D-looking globe. Objects near the edges will be distorted.

    **This is a _perspective_ projection, so it requires the following `kwargs` when creating the plot: `lat`, `lon`, and `dt`**. _The perspective of the globe will be based on these values._
    """

    ROBINSON = "robinson"
    """Good for showing the entire celestial sphere in one plot"""

    LAMBERT_AZ_EQ_AREA = "lambert_az_eq_area"
    """Lambert Azimuthal Equal-Area projection - accurately shows area, but distorts angles."""

    STEREOGRAPHIC = "stereographic"
    """
    Similar to the North/South Stereographic projection, but this version is location-dependent.

    **This is a _perspective_ projection, so it requires the following `kwargs` when creating the plot: `lat`, `lon`, and `dt`**. _The perspective of the map will be based on these values._
    """

    ZENITH = "zenith"
    """
    **This is a _perspective_ projection, so it requires the following `kwargs` when creating the plot: `lat`, `lon`, and `dt`**. _The perspective of the map will be based on these values._

    The Zenith projection shows the whole sky as seen from a specific time and place. They're also sometimes called "star charts" but that name is used for many different types of star maps, so Starplot uses the more specific name "Zenith plot" (which reflects the fact that the [zenith](https://en.wikipedia.org/wiki/Zenith) is in the center of the chart).
    """

    @staticmethod
    def crs(projection, center_lon=-180, **kwargs):
        projections = {
            Projection.STEREO_NORTH: ccrs.NorthPolarStereo,
            Projection.STEREO_SOUTH: ccrs.SouthPolarStereo,
            Projection.LAMBERT_AZ_EQ_AREA: ccrs.LambertAzimuthalEqualArea,
            Projection.MERCATOR: ccrs.Mercator,
            Projection.MOLLWEIDE: ccrs.Mollweide,
            Projection.MILLER: ccrs.Miller,
            Projection.ORTHOGRAPHIC: ccrs.Orthographic,
            Projection.ROBINSON: ccrs.Robinson,
            Projection.STEREOGRAPHIC: ccrs.Stereographic,
            Projection.ZENITH: ccrs.Stereographic,
        }
        proj_class = projections.get(projection)
        if projection in [
            Projection.ORTHOGRAPHIC,
            Projection.STEREOGRAPHIC,
            Projection.ZENITH,
        ]:
            return proj_class(
                central_longitude=kwargs["lon"], central_latitude=kwargs["lat"]
            )
        else:
            if kwargs.get("center_lat") is not None:
                kwargs["central_latitude"] = kwargs.pop("center_lat")

            return proj_class(center_lon, **kwargs)
