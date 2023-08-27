import pyproj

from starplot.data import constants


def create_ecliptic_line(num_points=50, ndigits=4) -> list:
    """
    A wonky way of creating a list of ra/dec points of the ecliptic:

    1. Use pyproj to create a "Great Circle" in lat/lon
    2. Convert list of lat/lon to ra/dec

    """
    incline = constants.ECLIPTIC_ANGLE
    g = pyproj.Geod(ellps="WGS84")

    radecs = []
    sections = [
        [0, 0, 90, -1 * incline],
        [90, -1 * incline, 180, 0],
        [180, 0, 270, incline],
        [270, incline, 360, 0],
    ]
    for section in sections:
        lonlats = g.npts(*section, num_points, initial_idx=0, terminus_idx=0)

        for lon, lat in lonlats:
            ra = round(((-1 * lon) + 360) / 15, ndigits)
            dec = round(lat, ndigits)
            radecs.append((ra, dec))

    return radecs


print(create_ecliptic_line())
