"""
This file is used as a 'scratchpad' during development for testing plots.
"""

import time
from datetime import datetime

from pytz import timezone
from matplotlib import patches
from starplot import Star, DSO, Constellation
from starplot.styles import PlotStyle, extensions, PolygonStyle
from starplot.map import Projection

import starplot as sp

start_time = time.time()

p = sp.MapPlot(
    projection=Projection.MILLER,
    ra_min=3,
    ra_max=9,
    dec_min=-16,
    dec_max=40,
    style=PlotStyle().extend(
        # extensions.GRAYSCALE,
        # extensions.GRAYSCALE_DARK,
        extensions.BLUE_LIGHT,
        # extensions.BLUE_MEDIUM,
        # extensions.BLUE_DARK,
        extensions.MAP,
    ),
    resolution=2000,
)

p.stars(where=[Star.magnitude < 4], labels=None)
p.constellations()
p.constellation_borders()

con = "gem"
orion = Constellation.get(iau_id=con)
print(len(p.objects.stars))
orion_stars = [s for s in p.objects.stars if s.constellation_id == con]
print(len(orion_stars))

from shapely import voronoi_polygons, GeometryCollection, MultiPoint, intersection

points = MultiPoint([(s.ra, s.dec) for s in orion_stars])

polygons = voronoi_polygons(
    geometry=points,
    # extend_to=orion.boundary.buffer(0.2),
    tolerance=2,
)

for polygon in polygons.geoms:
    # if not orion.boundary.contains(polygon.reverse()): continue
    inter = intersection(polygon, orion.boundary)
    if inter.geom_type == "Polygon":
        p.polygon(
            geometry=inter,
            style__edge_color="red",
        )
p.export("temp/voronoi.png")

# print(Star.get(name="Sirius").hip)
# print(DSO.all(2))

# print(Star.all(1))
# d = DSO.get(type="Open Cluster")
# print(d)

print(time.time() - start_time)
