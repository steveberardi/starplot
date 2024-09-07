from shapely.geometry import Polygon

from starplot import geod, utils


def circle(center, diameter_degrees):
    points = geod.ellipse(
        center,
        diameter_degrees,
        diameter_degrees,
        angle=0,
        num_pts=100,
    )
    points = [(round(24-utils.lon_to_ra(lon), 4), round(dec, 4)) for lon, dec in points]
    return Polygon(points)

