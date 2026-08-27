"""
Renders every map projection available in Starplot, showing only gridlines and
the Tissot indicatrix (a grid of same-size circles on the sky) so the shape,
size, and area distortion introduced by each projection is easy to compare.

Each projection uses the largest extent that stays reasonably sized -- pushed
right up to (but not past) the point where the projection's scale starts
blowing up toward infinity (e.g. Mercator/Miller near the poles, or any
azimuthal projection near its antipode).

"""

from pathlib import Path

from starplot import (
    Equidistant,
    Gnomonic,
    LambertAzEqArea,
    MapPlot,
    Mercator,
    Miller,
    Mollweide,
    ObliqueMercator,
    Orthographic,
    PlateCarree,
    Robinson,
    Stereographic,
    StereoNorth,
    StereoSouth,
    geometry,
)
from starplot.styles import PlotStyle, extensions

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "images" / "reference"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

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
    # Gnomonic projects the sphere from its own center onto a tangent
    # plane, so it can only show strictly *less* than a hemisphere -- at
    # exactly 90 degrees from center (a 180-degree-diameter circle) the
    # projection shoots off to infinity, so this needs to stay under that.
    # dec_min is also set here (rather than left at the dict() default of
    # -90) so the plot doesn't count as a "global extent" -- that skips
    # recalculating the true visible dec range from the clip circle, and
    # gridlines() then draws meridians all the way from -90 to 90, which
    # crosses straight through gnomonic's blow-up boundary and drops the
    # RA gridlines entirely (their points literally project to infinity).
    (
        "gnomonic",
        Gnomonic(center_dec=90),
        dict(dec_min=0),
        geometry.circle(center=(180, 90), diameter_degrees=120, num_pts=100),
    ),
    # Orthographic shows the sky as seen from infinitely far away, like a
    # view of the globe -- it can only show one hemisphere (up to 90 degrees
    # from center) at a time, but unlike Gnomonic/Stereographic it doesn't
    # need a manual clip circle: it knows its own visible-hemisphere bounds,
    # so the default dict()/no-clip_path extent below is enough on its own.
    ("orthographic", Orthographic(), dict(), None),
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
    p.export(str(OUTPUT_DIR / f"projection_{name}.svg"))
