from starplot import (
    MapPlot,
    Miller,
    StereoNorth,
    StereoSouth,
    Constellation,
    Star,
    CollisionHandler,
    _,
)
from starplot.styles import (
    PlotStyle,
    extensions,
    PolygonStyle,
    AnchorPointEnum,
    PathStyle,
)

from shapely import Polygon

style = PlotStyle().extend(
    extensions.STARPLOT,
    extensions.MAP,
    extensions.FIGURE_TRANSPARENT,
)

style.axes.border = None


constellation = Constellation.get(iau_id="gem")

ra, dec = [p for p in constellation.border.coords.xy]
extent = (min(ra) - 2, max(min(dec) - 2, -90), max(ra) + 2, min(max(dec) + 2, 90))

if constellation.dec > 50:
    proj = StereoNorth
elif constellation.dec < -60:
    proj = StereoSouth
else:
    proj = Miller

if extent[0] < 0:
    extent = (extent[0] + 360, extent[1], extent[2] + 360, extent[3])

center_ra = (extent[0] + extent[2]) / 2
if center_ra < 0:
    center_ra += 360
elif center_ra > 360:
    center_ra -= 360

p = MapPlot(
    projection=proj(center_ra=center_ra),
    ra_min=extent[0],
    ra_max=extent[2],
    dec_min=extent[1],
    dec_max=extent[3],
    style=style,
    clip_path=Polygon(constellation.border.coords),
    resolution=800,
    scale=1.05,
)

p.constellations(where=[_.iau_id == constellation.iau_id])


p.stars(
    where=[_.hip.isin(constellation.star_hip_ids)],
    where_labels=[False],
    # size_fn=lambda s: 30,
    style__marker__symbol="star",
    # style__marker__stroke="#fff",
    style__marker__stroke_width=0,
)

p.export(f"{constellation.iau_id}.svg")
