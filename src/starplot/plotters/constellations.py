import geopandas as gpd
import numpy as np

from starplot.coordinates import CoordinateSystem
from starplot.data import DataFiles, constellations as condata, stars
from starplot.data.constellations import CONSTELLATIONS_FULL_NAMES
from starplot.models.constellation import from_tuple as constellation_from_tuple
from starplot.projections import Projection
from starplot.styles import PathStyle, LineStyle
from starplot.styles.helpers import use_style
from starplot.utils import points_on_line
from starplot.utils import lon_to_ra, ra_to_lon


class ConstellationPlotterMixin:
    @use_style(PathStyle, "constellation")
    def constellations(
        self,
        style: PathStyle = None,
        labels: dict[str, str] = CONSTELLATIONS_FULL_NAMES,
        where: list = None,
    ):
        """Plots the constellation lines and/or labels.

        **Important:** If you're plotting the constellation lines, then it's good to plot them _first_, because Starplot will use the constellation lines to determine where to place labels that are plotted afterwards (labels will look better if they're not crossing a constellation line).

        Args:
            style: Styling of the constellations. If None, then the plot's style (specified when creating the plot) will be used
            labels: A dictionary where the keys are each constellation's 3-letter abbreviation, and the values are how the constellation will be labeled on the plot.
            where: A list of expressions that determine which constellations to plot. See [Selecting Objects](/reference-selecting-objects/) for details.
        """
        self.logger.debug("Plotting constellations...")

        labels = labels or {}
        labels_to_plot = {}
        where = where or []

        constellations_gdf = gpd.read_file(
            DataFiles.CONSTELLATIONS.value,
            engine="pyogrio",
            use_arrow=True,
            bbox=self._extent_mask(),
        )
        stars_df = stars.load("hipparcos")

        if constellations_gdf.empty:
            return

        if getattr(self, "projection", None) in [
            Projection.MERCATOR,
            Projection.MILLER,
        ]:
            transform = self._plate_carree
        else:
            transform = self._geodetic

        conline_hips = condata.lines()
        style_kwargs = style.line.matplot_kwargs(self.scale)

        for c in constellations_gdf.itertuples():
            obj = constellation_from_tuple(c)

            if not all([e.evaluate(obj) for e in where]):
                continue

            hiplines = conline_hips[c.iau_id]
            inbounds = False

            for s1_hip, s2_hip in hiplines:
                s1 = stars_df.loc[s1_hip]
                s2 = stars_df.loc[s2_hip]

                s1_ra = s1.ra_hours * 15
                s2_ra = s2.ra_hours * 15

                s1_dec = s1.dec_degrees
                s2_dec = s2.dec_degrees

                if s1_ra - s2_ra > 60:
                    s2_ra += 360

                elif s2_ra - s1_ra > 60:
                    s1_ra += 360

                if self.in_bounds(s1_ra / 15, s1_dec):
                    inbounds = True

                if self._coordinate_system == CoordinateSystem.RA_DEC:
                    s1_ra *= -1
                    s2_ra *= -1
                    x1, x2 = s1_ra, s2_ra
                    y1, y2 = s1_dec, s2_dec
                elif self._coordinate_system == CoordinateSystem.AZ_ALT:
                    x1, y1 = self._prepare_coords(s1_ra / 15, s1_dec)
                    x2, y2 = self._prepare_coords(s2_ra / 15, s2_dec)
                else:
                    raise ValueError("Unrecognized coordinate system")

                constellation_line = self.ax.plot(
                    [x1, x2],
                    [y1, y2],
                    transform=transform,
                    **style_kwargs,
                    clip_on=True,
                    clip_path=self._background_clip_path,
                    gid="constellations-line",
                )[0]

                extent = constellation_line.get_window_extent(
                    renderer=self.fig.canvas.get_renderer()
                )

                if extent.xmin < 0:
                    continue

                start = self._proj.transform_point(x1, y1, self._geodetic)
                end = self._proj.transform_point(x2, y2, self._geodetic)
                radius = style_kwargs.get("linewidth") or 1

                if any([np.isnan(n) for n in start + end]):
                    continue

                for x, y in points_on_line(start, end, 25):
                    x0, y0 = self.ax.transData.transform((x, y))
                    if x0 < 0 or y0 < 0:
                        continue
                    self._constellations_rtree.insert(
                        0,
                        np.array((x0 - radius, y0 - radius, x0 + radius, y0 + radius)),
                        obj=obj.name,
                    )

            if inbounds:
                self._objects.constellations.append(obj)
                labels_to_plot[obj.iau_id] = labels.get(obj.iau_id)

        self._plot_constellation_labels(style.label, labels_to_plot)

    def _plot_constellation_labels(
        self,
        style: PathStyle = None,
        labels: dict[str, str] = CONSTELLATIONS_FULL_NAMES,
    ):
        style = style or self.style.constellation.label

        for con in condata.iterator():
            _, ra, dec = condata.get(con)
            text = labels.get(con.lower())
            self.text(
                text,
                ra,
                dec,
                style,
                hide_on_collision=False,
                # hide_on_collision=self.hide_colliding_labels,
                gid="constellations-label-name",
            )

    @use_style(LineStyle, "constellation_borders")
    def constellation_borders(self, style: LineStyle = None):
        """Plots the constellation borders

        Args:
            style: Styling of the constellation borders. If None, then the plot's style (specified when creating the plot) will be used
        """
        extent = self._extent_mask()
        extent = (
            ra_to_lon(24 - self.ra_min),
            self.dec_min,
            ra_to_lon(24 - self.ra_max),
            self.dec_max,
        )

        constellation_borders = gpd.read_file(
            DataFiles.CONSTELLATION_BORDERS.value,
            engine="pyogrio",
            use_arrow=True,
            bbox=extent,
            # bbox=self._extent_mask(),
            # TODO : fix bbox here
        )

        if constellation_borders.empty:
            return

        geometries = []

        for _, c in constellation_borders.iterrows():
            for ls in c.geometry.geoms:
                geometries.append(ls)

        for ls in geometries:
            x, y = ls.xy
            x = list(x)
            y = list(y)

            x = [24 - (x0 / 15) for x0 in x]

            # if self._coordinate_system == CoordinateSystem.RA_DEC:
            #     x_coords = list(x)
            #     y_coords = list(y)

            # elif self._coordinate_system == CoordinateSystem.AZ_ALT:
            #     x_coords = []
            #     y_coords = []

            #     for r, d in zip(x, y):
            #         az, alt = self._prepare_coords(r / 15, d)
            #         x_coords.append(az)
            #         y_coords.append(alt)
            # else:
            #     raise ValueError("Unrecognized coordinate system")

            self.line(
                coordinates=zip(x, y),
                style=style,
            )

            # self.ax.plot(
            #     x_coords,
            #     y_coords,
            #     transform=self._plate_carree,
            #     clip_on=True,
            #     clip_path=self._background_clip_path,
            #     gid="constellations-border",
            #     **style_kwargs,
            # )

    def _constellation_borders(self):
        from shapely import LineString, MultiLineString, Polygon
        from shapely.ops import unary_union

        constellation_borders = gpd.read_file(
            DataFiles.CONSTELLATIONS.value,
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
