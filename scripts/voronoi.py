import time
from datetime import datetime

from shapely import (
    voronoi_polygons,
    GeometryCollection,
    MultiPoint,
    intersection,
    normalize,
    delaunay_triangles,
    distance,
)
from pytz import timezone
from matplotlib import patches
from starplot import Star, DSO, Constellation
from starplot.styles import PlotStyle, extensions, PolygonStyle
from starplot.map import Projection

import starplot as sp

start_time = time.time()

p = sp.MapPlot(
    projection=Projection.MILLER,
    # projection=Projection.STEREO_NORTH,
    ra_min=1,
    ra_max=18,
    dec_min=-40,
    dec_max=60,
    style=PlotStyle().extend(
        extensions.GRAYSCALE,
        # extensions.GRAYSCALE_DARK,
        # extensions.BLUE_LIGHT,
        # extensions.BLUE_MEDIUM,
        # extensions.BLUE_DARK,
        extensions.MAP,
        {
            "constellation": {
                "label": {
                    "font_size": 5,
                }
            }
        },
    ),
    resolution=4000,
)

p.stars(where=[Star.magnitude < 6], labels=None)  # , size_fn=lambda s: 20)
p.constellations()
p.constellation_borders()

print(len(p.objects.stars))

p.export("temp/voronoi.png")
# exit()
for constellation in p.objects.constellations:
    # con = "gem"
    # constellation = Constellation.get(iau_id=con)
    print(constellation.name)
    constellation_stars = [
        s for s in p.objects.stars if s.constellation_id == constellation.iau_id
    ]
    print(len(constellation_stars))

    points = MultiPoint([(s.ra, s.dec) for s in constellation_stars])

    v = voronoi_polygons(
        geometry=points,
        # extend_to=orion.boundary.buffer(0.2),
        tolerance=2,
    )
    triangles = delaunay_triangles(
        geometry=points,
        tolerance=3,
    )

    # for polygon in polygons.geoms:
    #     # if not orion.boundary.contains(polygon.reverse()): continue
    #     inter = intersection(polygon, constellation.boundary)
    #     if inter.geom_type == "Polygon":
    #         p.polygon(
    #             geometry=inter,
    #             style__edge_color="red",
    #         )

    polygons = []
    for t in triangles.geoms:
        # if not orion.boundary.contains(polygon.reverse()): continue
        try:
            inter = intersection(t, constellation.boundary)
        except:
            continue
        if (
            inter.geom_type == "Polygon"
            and len(list(zip(*inter.exterior.coords.xy))) > 2
        ):
            # continue
            # p.polygon(
            #     geometry=inter,
            #     style__edge_color="blue",
            #     style__alpha=0.13,
            # )
            polygons.append(inter)

    p_by_area = {pg.area: pg for pg in polygons}
    polygons_sorted = [p_by_area[k] for k in sorted(p_by_area.keys(), reverse=True)]

    """
        TODO: Turn this into a function on map plot class
    """

    constellation_centroid = constellation.boundary.centroid

    def sort_wrapper(text):
        def sorter(g):
            d = distance(g.centroid, points.centroid)
            # d = distance(g.centroid, constellation.boundary.centroid)
            extent = abs(g.bounds[2] - g.bounds[0])
            area = g.area / constellation.boundary.area
            # return area + (extent * len(text)/20)
            return ((extent) - (d / 2)) * area**10

        return sorter

    # sort by combination of horizontal extent and area
    polygons_sorted = sorted(
        polygons_sorted, key=sort_wrapper(constellation.name), reverse=True
    )

    # p_sort_distance_to_center = sorted(polygons_sorted, key=lambda pg: distance(pg.centroid, points.centroid))

    i = 0

    p.polygon(
        geometry=polygons_sorted[i],
        style__fill_color="green",
        style__alpha=0.23,
    )
    p.marker(
        polygons_sorted[i].centroid.x,
        polygons_sorted[i].centroid.y,
        label=None,
        style__marker__symbol="circle_cross",
        style__marker__size=9,
        style__marker__color="red",
        style__marker__edge_color="red",
        style__marker__edge_width=6,
    )

    for big_p in polygons_sorted:
        # continue
        # if big_p.area < constellation.boundary.area/2:
        p.polygon(
            geometry=big_p,
            style__edge_color="green",
            style__alpha=0.23,
        )


p.export("temp/voronoi.png")

# print(Star.get(name="Sirius").hip)
# print(DSO.all(2))

# print(Star.all(1))
# d = DSO.get(type="Open Cluster")
# print(d)

print(time.time() - start_time)
