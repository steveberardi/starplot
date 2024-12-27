import geopandas as gpd
import numpy as np

import rtree
from shapely import (
    MultiPoint,
)

from starplot.coordinates import CoordinateSystem
from starplot.data import DataFiles, constellations as condata, stars
from starplot.data.constellations import (
    CONSTELLATIONS_FULL_NAMES,
    CONSTELLATION_HIP_IDS,
)
from starplot.models.constellation import from_tuple as constellation_from_tuple
from starplot.projections import Projection
from starplot.styles import PathStyle, LineStyle
from starplot.styles.helpers import use_style
from starplot.utils import points_on_line
from starplot.geometry import wrapped_polygon_adjustment


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
        where = where or []
        ctr = 0

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
        constellation_points_to_index = []

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

                if self.in_bounds(s1_ra / 15, s1_dec) and self.in_bounds(
                    s2_ra / 15, s2_dec
                ):
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
                    clip_on=True,
                    clip_path=self._background_clip_path,
                    gid="constellations-line",
                    **style_kwargs,
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
                    display_x, display_y = self.ax.transData.transform((x, y))
                    if display_x < 0 or display_y < 0:
                        continue
                    constellation_points_to_index.append(
                        (
                            ctr,
                            (
                                display_x - radius,
                                display_y - radius,
                                display_x + radius,
                                display_y + radius,
                            ),
                            None,
                        )
                    )
                    ctr += 1

            if inbounds:
                self._objects.constellations.append(obj)

        if self._constellations_rtree.get_size() == 0:
            self._constellations_rtree = rtree.index.Index(
                constellation_points_to_index
            )
        else:
            for bbox in constellation_points_to_index:
                self._constellations_rtree.insert(
                    0,
                    bbox,
                    None,
                )
        # self._plot_constellation_labels(style.label, labels_to_plot)
        # self._plot_constellation_labels_experimental(style.label, labels_to_plot)

    def _plot_constellation_labels(
        self,
        style: PathStyle = None,
        labels: dict[str, str] = CONSTELLATIONS_FULL_NAMES,
    ):
        """
        TODO:
        1. plot label, if removed then get size in display coords
        2. generate random points in polygon, convert to display coords, test for intersections
        3. plot best score

        problem = constellations usually plotted first, so wont have star data (or could use stars from constellations only?)

        constellation names CAN cross lines but not stars

        """
        style = style or self.style.constellation.label
        self._constellation_labels = []

        for con in condata.iterator():
            _, ra, dec = condata.get(con)
            text = labels.get(con.lower())
            label = self.text(
                text,
                ra,
                dec,
                style,
                hide_on_collision=False,
                # hide_on_collision=self.hide_colliding_labels,
                gid="constellations-label-name",
            )
            if label is not None:
                self._constellation_labels.append(label)

    @use_style(LineStyle, "constellation_borders")
    def constellation_borders(self, style: LineStyle = None):
        """Plots the constellation borders

        Args:
            style: Styling of the constellation borders. If None, then the plot's style (specified when creating the plot) will be used
        """
        constellation_borders = self._read_geo_package(
            DataFiles.CONSTELLATION_BORDERS.value
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

            if self._coordinate_system == CoordinateSystem.RA_DEC:
                self.ax.plot(
                    x,
                    y,
                    transform=self._plate_carree,
                    clip_on=True,
                    clip_path=self._background_clip_path,
                    gid="constellations-border",
                    **style.matplot_kwargs(self.scale),
                )

            elif self._coordinate_system == CoordinateSystem.AZ_ALT:
                x = [24 - (x0 / 15) for x0 in x]

                self.line(
                    coordinates=zip(x, y),
                    style=style,
                )

            else:
                raise ValueError("Unrecognized coordinate system")

    def constellation_labels(
        self,
        style: PathStyle = None,
        labels: dict[str, str] = CONSTELLATIONS_FULL_NAMES,
        auto_adjust: bool = True,
    ):
        """
        Plots constellation labels

        TODO:
            make this work without plotting constellations first
        """
        self.logger.debug("Plotting constellation labels...")

        for constellation in self.objects.constellations:
            constellation_line_stars = [
                s
                for s in self.objects.stars
                if s.constellation_id == constellation.iau_id
                and s.hip in CONSTELLATION_HIP_IDS[constellation.iau_id]
            ]
            if not constellation_line_stars:
                continue

            points_line = MultiPoint([(s.ra, s.dec) for s in constellation_line_stars])
            centroid = points_line.centroid

            adjustment = wrapped_polygon_adjustment(constellation.boundary)

            if (adjustment > 0 and centroid.x < 12) or (
                adjustment < 0 and centroid.x > 12
            ):
                x = centroid.x + adjustment
            else:
                x = centroid.x

            text = labels.get(constellation.iau_id)
            style = style or self.style.constellation.label
            style.anchor_point = "center"
            self.text(
                text,
                x,
                centroid.y,
                style,
                hide_on_collision=self.hide_colliding_labels,
                area=constellation.boundary,
            )
