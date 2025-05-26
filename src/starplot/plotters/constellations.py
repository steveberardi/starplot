import numpy as np

import rtree
from shapely import (
    MultiPoint,
)
from matplotlib.collections import LineCollection
from ibis import _

from starplot.coordinates import CoordinateSystem
from starplot.data import constellations as condata, constellation_lines as conlines
from starplot.data.stars import load as load_stars, StarCatalog
from starplot.data.constellations import (
    CONSTELLATIONS_FULL_NAMES,
)
from starplot.data.constellation_stars import CONSTELLATION_HIPS
from starplot.models import Star
from starplot.models.constellation import from_tuple as constellation_from_tuple
from starplot.projections import Projection
from starplot.profile import profile
from starplot.styles import PathStyle, LineStyle, LabelStyle
from starplot.styles.helpers import use_style
from starplot.utils import points_on_line
from starplot.geometry import is_wrapped_polygon

DEFAULT_AUTO_ADJUST_SETTINGS = {
    "avoid_constellation_lines": False,
    "point_generation_max_iterations": 10,
    "distance_step_size": 2,
    "max_distance": 3_000,
    "label_padding": 6,
    "buffer": 0.3,
    "seed": None,
}
"""Default settings for auto-adjusting constellation labels"""


class ConstellationPlotterMixin:
    def inbounds_temp(self, x, y):
        data_x, data_y = self._proj.transform_point(x, y, self._geodetic)
        display_x, display_y = self.ax.transData.transform((data_x, data_y))
        return display_x > 0 and display_y > 0

    @profile
    def _prepare_constellation_stars(self) -> dict[int, tuple[float, float]]:
        """
        Returns dictionary of stars and their position:

        {hip: (x,y)}

        Where (x, y) is the plotted coordinate system (RA/DEC or AZ/ALT)
        """
        results = load_stars(
            catalog=StarCatalog.BIG_SKY_MAG11,
            filters=[_.hip.isin(CONSTELLATION_HIPS)],
        )
        df = results.to_pandas()
        df = self._prepare_star_coords(df, limit_by_altaz=False)

        return {star.hip: (star.x, star.y) for star in df.itertuples()}

    @profile
    @use_style(LineStyle, "constellation_lines")
    def constellations(
        self,
        style: LineStyle = None,
        where: list = None,
        sql: str = None,
    ):
        """Plots the constellation lines **only**. To plot constellation borders and/or labels, see separate functions for them.

        **Important:** If you're plotting the constellation lines, then it's good to plot them _first_, because Starplot will use the constellation lines to determine where to place labels that are plotted afterwards (labels will look better if they're not crossing a constellation line).

        Args:
            style: Styling of the constellations. If None, then the plot's style (specified when creating the plot) will be used
            where: A list of expressions that determine which constellations to plot. See [Selecting Objects](/reference-selecting-objects/) for details.
            sql: SQL query for selecting constellations (table name is `_`). This query will be applied _after_ any filters in the `where` kwarg.
        """
        self.logger.debug("Plotting constellation lines...")

        where = where or []
        ctr = 0

        extent = self._extent_mask()
        results = condata.load(extent=extent, filters=where, sql=sql)
        constellations_df = results.to_pandas()

        if constellations_df.empty:
            return

        if getattr(self, "projection", None) in [
            Projection.MERCATOR,
            Projection.MILLER,
        ]:
            transform = self._plate_carree
        else:
            transform = self._geodetic

        style_kwargs = style.matplot_kwargs(self.scale)
        constellation_points_to_index = []
        lines = []
        constars = self._prepare_constellation_stars()

        for c in constellations_df.itertuples():
            hiplines = conlines.hips[c.iau_id]
            inbounds = False

            for s1_hip, s2_hip in hiplines:
                if not constars.get(s2_hip):
                    continue
                s1_ra, s1_dec = constars.get(s1_hip)
                s2_ra, s2_dec = constars.get(s2_hip)

                if s1_ra - s2_ra > 60:
                    s2_ra += 360
                elif s2_ra - s1_ra > 60:
                    s1_ra += 360

                x1, x2 = s1_ra, s2_ra
                y1, y2 = s1_dec, s2_dec
                if not inbounds and (
                    self._in_bounds_xy(x1, y1) or self._in_bounds_xy(x2, y2)
                ):
                    inbounds = True
                elif not inbounds:
                    continue

                if self._coordinate_system == CoordinateSystem.RA_DEC:
                    x1 *= -1
                    x2 *= -1

                lines.append([(x1, y1), (x2, y2)])

                start = self._proj.transform_point(x1, y1, self._geodetic)
                end = self._proj.transform_point(x2, y2, self._geodetic)
                radius = style.width or 1

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
                obj = constellation_from_tuple(c)
                self._objects.constellations.append(obj)

        style_kwargs = style.matplot_line_collection_kwargs(self.scale)

        line_collection = LineCollection(
            lines,
            **style_kwargs,
            transform=transform,
            clip_on=True,
            clip_path=self._background_clip_path,
            gid="constellations-line",
        )

        self.ax.add_collection(line_collection)

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

    @profile
    @use_style(LineStyle, "constellation_borders")
    def constellation_borders(self, style: LineStyle = None):
        """Plots the constellation borders

        Args:
            style: Styling of the constellation borders. If None, then the plot's style (specified when creating the plot) will be used
        """
        extent = self._extent_mask()
        results = condata.load_borders(extent=extent)
        borders_df = results.to_pandas()

        if borders_df.empty:
            return

        border_lines = []
        geometries = [line.geometry for line in borders_df.itertuples()]

        for ls in geometries:
            if ls.length < 80:
                ls = ls.segmentize(1)

            xy = [c for c in ls.coords]

            if self._coordinate_system == CoordinateSystem.RA_DEC:
                border_lines.append(xy)

            elif self._coordinate_system == CoordinateSystem.AZ_ALT:
                coords = [self._prepare_coords(*p) for p in xy]
                border_lines.append(coords)

            else:
                raise ValueError("Unrecognized coordinate system")

        line_collection = LineCollection(
            border_lines,
            **style.matplot_line_collection_kwargs(self.scale),
            transform=self._crs,
            clip_on=True,
            clip_path=self._background_clip_path,
            gid="constellations-border",
        )
        self.ax.add_collection(line_collection)

    def _constellation_labels_auto(self, style, labels, settings):
        hips = []
        for c in self.objects.constellations:
            hips.extend(c.star_hip_ids)

        all_constellation_stars = Star.find(where=[_.hip.isin(hips)])

        for constellation in self.objects.constellations:
            constellation_line_stars = [
                s
                for s in all_constellation_stars
                if s.hip in constellation.star_hip_ids
            ]
            if not constellation_line_stars:
                continue

            if is_wrapped_polygon(constellation.boundary):
                starpoints = []
                ra, dec = zip(*[(s.ra, s.dec) for s in constellation_line_stars])
                new_ra = [r - 360 if r > 300 else r for r in ra]
                starpoints = list(zip(new_ra, dec))

            else:
                ra, dec = zip(*[(s.ra, s.dec) for s in constellation_line_stars])
                starpoints = list(zip(ra, dec))

            points_line = MultiPoint(starpoints)
            centroid = points_line.centroid
            text = labels.get(constellation.iau_id)

            self.text(
                text,
                centroid.x,
                centroid.y,
                style,
                hide_on_collision=self.hide_colliding_labels,
                area=constellation.boundary,  # TODO : make this intersection with clip path
                auto_adjust_settings=settings,
                gid="constellations-label-name",
            )

    def _constellation_labels_static(self, style, labels):
        for con in condata.iterator():
            _, ra, dec = condata.get(con)
            text = labels.get(con.lower())
            self.text(
                text,
                ra * 15,
                dec,
                style,
                hide_on_collision=self.hide_colliding_labels,
                remove_on_constellation_collision=False,
                gid="constellations-label-name",
            )

    @profile
    @use_style(LabelStyle, "constellation_labels")
    def constellation_labels(
        self,
        style: LabelStyle = None,
        labels: dict[str, str] = CONSTELLATIONS_FULL_NAMES,
        auto_adjust: bool = True,
        auto_adjust_settings: dict = DEFAULT_AUTO_ADJUST_SETTINGS,
    ):
        """
        Plots constellation labels for all constellations that have been plotted. This means you must plot the constellations before plotting their labels.

        It's good to plot these last because they're area-based labels (vs point-based, like for star names), and area-based labels have more freedom to move around. If you plot area-based labels first, then it would limit the available space for point-based labels.

        Args:
            style: Styling of the constellation labels. If None, then the plot's style (specified when creating the plot) will be used
            labels: A dictionary where the keys are each constellation's 3-letter IAU abbreviation, and the values are how the constellation will be labeled on the plot.
            auto_adjust: If True (the default), then labels will be automatically adjusted to avoid collisions with other labels and stars **Important: you must plot stars and constellations first for this to work**. This uses a fairly simple method: for each constellation it finds the centroid of all plotted constellation stars with lines and then generates random points in the constellation boundary starting at the centroid and then progressively increasing the distance from the centroid.
            auto_adjust_settings: Optional settings for the auto adjustment algorithm.
        """

        if auto_adjust:
            settings = DEFAULT_AUTO_ADJUST_SETTINGS
            settings.update(auto_adjust_settings)
            self._constellation_labels_auto(style, labels, settings=settings)
        else:
            self._constellation_labels_static(style, labels)
