import geopandas as gpd

from shapely import MultiPolygon
from shapely import (
    MultiPoint,
    intersection,
    delaunay_triangles,
    distance,
)

from starplot.data import DataFiles
from starplot.data.constellations import (
    CONSTELLATIONS_FULL_NAMES,
    CONSTELLATION_HIP_IDS,
)
from starplot.styles import PathStyle


class ExperimentalPlotterMixin:
    def _constellation_borders(self):
        from shapely import LineString, MultiLineString
        from shapely.ops import unary_union

        constellation_borders = gpd.read_file(
            DataFiles.CONSTELLATIONS,
            engine="pyogrio",
            use_arrow=True,
            bbox=self._extent_mask(),
        )

        if constellation_borders.empty:
            return

        geometries = []

        for i, constellation in constellation_borders.iterrows():
            geometry_types = constellation.geometry.geom_type

            # equinox = LineString([[0, 90], [0, -90]])
            """
            Problems:
                - Need to handle multipolygon borders too (SER)
                - Shapely's union doesn't handle geodesy (e.g. TRI + AND)
                - ^^ TRI is plotted with ra < 360, but AND has ra > 360
                - ^^ idea: create union first and then remove duplicate lines?
            
                TODO: create new static data file of constellation border lines
            """

            if "Polygon" in geometry_types and "MultiPolygon" not in geometry_types:
                polygons = [constellation.geometry]

            elif "MultiPolygon" in geometry_types:
                polygons = constellation.geometry.geoms

            for p in polygons:
                coords = list(zip(*p.exterior.coords.xy))
                # coords = [(ra * -1, dec) for ra, dec in coords]

                new_coords = []

                for i, c in enumerate(coords):
                    ra, dec = c
                    if i > 0:
                        if new_coords[i - 1][0] - ra > 60:
                            ra += 360

                        elif ra - new_coords[i - 1][0] > 60:
                            new_coords[i - 1][0] += 360

                    new_coords.append([ra, dec])

                ls = LineString(new_coords)
                geometries.append(ls)

        mls = MultiLineString(geometries)
        geometries = unary_union(mls)

        for ls in list(geometries.geoms):
            x, y = ls.xy

            self.line(zip(x, y), self.style.constellation_borders)
            # x, y = ls.xy
            # newx = [xx * -1 for xx in list(x)]
            # self.ax.plot(
            #     # list(x),
            #     newx,
            #     list(y),
            #     # **self._plot_kwargs(),
            #     # transform=self._geodetic,
            #     transform=self._plate_carree,
            #     **style_kwargs,
            # )

    def _plot_constellation_labels_experimental(
        self,
        style: PathStyle = None,
        labels: dict[str, str] = CONSTELLATIONS_FULL_NAMES,
    ):
        def sorter(g):
            # higher score is better
            d = distance(g.centroid, points_line.centroid)
            # d = distance(g.centroid, constellation.boundary.centroid)
            extent = abs(g.bounds[2] - g.bounds[0])
            area = g.area / constellation.boundary.area
            # return ((extent**3)) * area**2
            # return ((extent**2) - (d/2)) * area**2
            # print(str(extent) + " " + str(area) + " " + str(d))
            return d**2 * -1
            return (extent / 2 + area) - (d / 5)

        for constellation in self.objects.constellations:
            constellation_stars = [
                s
                for s in self.objects.stars
                if s.constellation_id == constellation.iau_id and s.magnitude < 5
            ]
            constellation_line_stars = [
                s
                for s in self.objects.stars
                if s.constellation_id == constellation.iau_id
                and s.hip in CONSTELLATION_HIP_IDS[constellation.iau_id]
            ]
            points = MultiPoint([(s.ra, s.dec) for s in constellation_stars])
            points_line = MultiPoint([(s.ra, s.dec) for s in constellation_line_stars])

            triangles = delaunay_triangles(
                geometry=points,
                tolerance=2,
            )
            print(constellation.name + " " + str(len(triangles.geoms)))

            polygons = []
            for t in triangles.geoms:
                try:
                    inter = intersection(t, constellation.boundary)
                except Exception:
                    continue
                if (
                    inter.geom_type == "Polygon"
                    and len(list(zip(*inter.exterior.coords.xy))) > 2
                ):
                    polygons.append(inter)

            p_by_area = {pg.area: pg for pg in polygons}
            polygons_sorted = [
                p_by_area[k] for k in sorted(p_by_area.keys(), reverse=True)
            ]

            # sort by combination of horizontal extent and area
            polygons_sorted = sorted(polygons_sorted, key=sorter, reverse=True)

            if len(polygons_sorted) > 0:
                i = 0
                ra, dec = polygons_sorted[i].centroid.x, polygons_sorted[i].centroid.y
            else:
                ra, dec = constellation.ra, constellation.dec

            text = labels.get(constellation.iau_id)
            style = style or self.style.constellation.label
            style.anchor_point = "center"
            self.text(
                text,
                ra,
                dec,
                style,
                hide_on_collision=self.hide_colliding_labels,
                area=MultiPolygon(polygons_sorted[:3])
                if len(polygons_sorted)
                else constellation.boundary,
            )
