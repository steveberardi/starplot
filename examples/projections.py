"""
Renders every map projection available in Starplot, showing only gridlines and
the Tissot indicatrix (a grid of same-size circles on the sky) so the shape,
size, and area distortion introduced by each projection is easy to compare.

Each projection uses the largest extent that stays reasonably sized -- pushed
right up to (but not past) the point where the projection's scale starts
blowing up toward infinity (e.g. Mercator/Miller near the poles, or any
azimuthal projection near its antipode).

"""

from starplot import (
    Equidistant,
    LambertAzEqArea,
    MapPlot,
    Mercator,
    Miller,
    Mollweide,
    ObliqueMercator,
    PlateCarree,
    Robinson,
    Stereographic,
    StereoNorth,
    StereoSouth,
    geometry,
)
from starplot.styles import PlotStyle, extensions

style = PlotStyle().extend(extensions.STARPLOT, extensions.MAP)

style.axes.border.width = 1
style.figure.background.fill = None
# axes.border isn't needed for these reference images, and its buffered clip
# geometry can come back as a MultiPolygon for some of the extreme circular
# extents below (e.g. StereoSouth) -- another pre-existing bug, unrelated to
# this script, that's simplest to just sidestep here.
# style.axes.border = None

# Azimuthal projections (StereoNorth/South, Stereographic, Equidistant,
# LambertAzEqArea) are centered on a point and distort worst near their
# antipode, so their extent is defined as a circle (in RA/DEC) around their
# center -- a rectangular RA/DEC extent would either leave the corners
# empty (for a polar center) or scale wildly unevenly (for an equatorial
# center). Stereographic's scale blows up to infinity at the antipode (it's
# conformal), so its circle is much smaller than Equidistant/LambertAzEqArea,
# which stay finite all the way to (almost) the antipode.
STEREO_RADIUS = 220  # degrees (diameter) -- used for StereoNorth/South/Stereographic
WIDE_AZIMUTHAL_RADIUS = (
    340  # degrees (diameter) -- used for Equidistant/LambertAzEqArea
)

# Each entry: (filename suffix, projection instance, extent kwargs for MapPlot,
# optional clip_path)
PROJECTIONS = [
    # Cylindrical projections: RA wraps all the way around, but declination
    # has to be capped before the poles, where these projections stretch
    # toward infinity (Mercator worst, Miller more forgiving, PlateCarree not
    # at all -- it's linear, so it can use the full -90...90 range).
    ("miller", Miller(), dict(dec_min=-85, dec_max=85), None),
    ("mercator", Mercator(), dict(dec_min=-80, dec_max=80), None),
    ("plate_carree", PlateCarree(), dict(dec_min=-90, dec_max=90), None),
    # Oblique Mercator is Mercator wrapped around an arbitrary great circle
    # (set by center_ra/center_dec + azimuth) instead of the equator, so
    # unlike plain Mercator its blow-up points aren't fixed at the poles --
    # they're always exactly 90 degrees from the center, in whichever two
    # directions are perpendicular to azimuth. A rectangular RA/DEC extent
    # can't dodge that (it's 2 points, not a dec band), so -- as with the
    # azimuthal projections below -- this uses a circle around the center,
    # sized well under that 90-degree radius.
    (
        "oblique_mercator",
        ObliqueMercator(azimuth=45),
        dict(),
        geometry.circle(center=(180, 0), diameter_degrees=150, num_pts=100),
    ),
    # Global-only projections always show the entire sky
    ("mollweide", Mollweide(), dict(), None),
    ("robinson", Robinson(), dict(), None),
    # Equal-area/equidistant azimuthal projections stay finite over (almost)
    # the entire sphere, so they can use a very wide circle.
    (
        "equidistant",
        Equidistant(),
        dict(),
        geometry.circle(
            center=(180, 0), diameter_degrees=WIDE_AZIMUTHAL_RADIUS, num_pts=100
        ),
    ),
    (
        "lambert_az_eq_area",
        LambertAzEqArea(),
        dict(),
        geometry.circle(
            center=(180, 0), diameter_degrees=WIDE_AZIMUTHAL_RADIUS, num_pts=100
        ),
    ),
    # Stereographic (conformal) projections blow up toward infinity at their
    # antipode, so they need a much smaller circle than the equal-area/
    # equidistant ones above.
    (
        "stereo_north",
        StereoNorth(),
        dict(),
        geometry.circle(center=(180, 90), diameter_degrees=STEREO_RADIUS, num_pts=100),
    ),
    (
        "stereo_south",
        StereoSouth(),
        dict(),
        geometry.circle(center=(180, -90), diameter_degrees=STEREO_RADIUS, num_pts=100),
    ),
    (
        "stereographic",
        Stereographic(),
        dict(),
        geometry.circle(center=(180, 0), diameter_degrees=STEREO_RADIUS, num_pts=100),
    ),
]

for name, projection, extent, clip_path in PROJECTIONS:
    kwargs = dict(ra_min=0, ra_max=360, dec_min=-90, dec_max=90)
    kwargs.update(extent)
    if clip_path is not None:
        kwargs["clip_path"] = clip_path

    p = MapPlot(
        projection=projection,
        style=style,
        resolution=1600,
        **kwargs,
    )
    p.gridlines(labels=False)
    p.tissot()
    p.export(f"projection_{name}.svg")
