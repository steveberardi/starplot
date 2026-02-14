from typing import Callable

import numpy as np

import rtree
from shapely import (
    MultiPoint,
)
from matplotlib.collections import LineCollection
from ibis import _

from starplot.coordinates import CoordinateSystem
from starplot.data import db, constellations as condata
from starplot.data.catalogs import (
    Catalog,
    CONSTELLATIONS_IAU,
    CONSTELLATION_BORDERS,
    BIG_SKY_MAG11,
)
from starplot.data.stars import load as load_stars
from starplot.models import Star, Constellation
from starplot.models.constellation import from_tuple
from starplot.projections import (
    StereoNorth,
    StereoSouth,
    Stereographic,
    Equidistant,
    LambertAzEqArea,
)
from starplot.profile import profile
from starplot.styles import LineStyle, LabelStyle
from starplot.styles.helpers import use_style
from starplot.geometry import is_wrapped_polygon, line_segment
from starplot.plotters.text import CollisionHandler

GEODETIC_PROJECTIONS = (
    Equidistant,
    LambertAzEqArea,
    Stereographic,
    StereoNorth,
    StereoSouth,
)


class ConstellationPlotterMixin:
    def inbounds_temp(self, x, y):
        data_x, data_y = self._proj.transform_point(x, y, self._geodetic)
        display_x, display_y = self.ax.transData.transform((data_x, data_y))
        return display_x > 0 and display_y > 0

    @profile
    def _prepare_constellation_stars(
        self, constellations: list[Constellation]
    ) -> dict[int, tuple[float, float]]:
        """
        Returns dictionary of stars and their position:

        {hip: (x,y)}

        Where (x, y) is the plotted coordinate system (RA/DEC or AZ/ALT)
        """
        hips = []
        for c in constellations:
            hips.extend(c.star_hip_ids)

        results = load_stars(
            catalog=BIG_SKY_MAG11,
            filters=[_.hip.isin(hips)],
        )
        results = results.select(
            "ra",
            "dec",
            "epoch_year",
            "hip",
            "parallax_mas",
            "ra_mas_per_year",
            "dec_mas_per_year",
        )
        df = results.to_pandas()
        df["ra_hours"], df["dec_degrees"] = (df.ra / 15, df.dec)
        df = self._prepare_star_coords(df, limit_by_altaz=False)

        return {star.hip: (star.x, star.y) for star in df.itertuples()}

    @profile
    @use_style(LineStyle, "constellation_lines")
    def constellations(
        self,
        style: LineStyle = None,
        where: list = None,
        sql: str = None,
        catalog: Catalog = CONSTELLATIONS_IAU,
    ):
        """Plots the constellation lines **only**. To plot constellation borders and/or labels, see separate functions for them.

        **Important:** If you're plotting the constellation lines, then it's good to plot them _first_, because Starplot will use the constellation lines to determine where to place labels that are plotted afterwards (labels will look better if they're not crossing a constellation line).

        Args:
            style: Styling of the constellations. If None, then the plot's style (specified when creating the plot) will be used
            where: A list of expressions that determine which constellations to plot. See [Selecting Objects](/reference-selecting-objects/) for details.
            sql: SQL query for selecting constellations (table name is `_`). This query will be applied _after_ any filters in the `where` kwarg.
            catalog: The catalog of constellations to use -- see [catalogs overview](/data/overview/) for details
        """
        self.logger.debug("Plotting constellation lines...")

        where = where or []
        ctr = 0

        extent = self._extent_mask()
        results = condata.load(extent=extent, filters=where, sql=sql, catalog=catalog)
        constellations_df = results.to_pandas()

        if constellations_df.empty:
            return

        constellations = [from_tuple(c) for c in constellations_df.itertuples()]

        projection = getattr(self, "projection", None)
        if isinstance(projection, GEODETIC_PROJECTIONS):
            transform = self._geodetic
        else:
            transform = self._plate_carree

        style_kwargs = style.matplot_kwargs(self.scale)
        constellation_points_to_index = []
        lines = []
        constars = self._prepare_constellation_stars(constellations)

        for c in constellations:
            hiplines = c.star_hip_lines
            inbounds = False

            for s1_hip, s2_hip in hiplines:
                if not constars.get(s1_hip) or not constars.get(s2_hip):
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
                radius = style.width * self.scale if style.width else 1

                if any([np.isnan(n) for n in start + end]):
                    continue

                display_start = self.ax.transData.transform(start)
                display_end = self.ax.transData.transform(end)

                if (
                    display_start[0] == display_end[0]
                    and display_start[1] == display_end[1]
                ):
                    continue

                for x, y in line_segment(display_start, display_end, radius * 4):
                    if x < 0 or y < 0:
                        continue
                    bbox = (
                        x - radius,
                        y - radius,
                        x + radius,
                        y + radius,
                    )
                    if self.debug_text:
                        self._debug_bbox(bbox, color="#39FF14", width=0.5)

                    constellation_points_to_index.append((ctr, bbox, None))
                    ctr += 1

            if inbounds:
                self._objects.constellations.append(c)

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

    @profile
    @use_style(LineStyle, "constellation_borders")
    def constellation_borders(
        self, style: LineStyle = None, catalog: Catalog = CONSTELLATION_BORDERS
    ):
        """Plots the constellation borders

        Args:
            style: Styling of the constellation borders. If None, then the plot's style (specified when creating the plot) will be used
            catalog: Catalog to use for constellation borders
        """
        con = db.connect()
        borders = catalog._load(connection=con, table_name="constellation_borders")
        borders = borders.mutate(
            geometry=_.geometry.cast("geometry"),  # cast WKB to geometry type
        )

        extent = self._extent_mask()
        borders_df = borders.filter(_.geometry.intersects(extent)).to_pandas()

        if borders_df.empty:
            return

        border_lines = []
        geometries = [line.geometry for line in borders_df.itertuples()]

        for ls in geometries:
            if ls.length < 360:
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

    @profile
    @use_style(LabelStyle, "constellation_labels")
    def constellation_labels(
        self,
        style: LabelStyle = None,
        label_fn: Callable[[Constellation], str] = Constellation.get_label,
        collision_handler: CollisionHandler = None,
    ):
        """
        Plots constellation labels for all constellations that have been plotted. This means you must plot the constellations before plotting their labels.

        It's good to plot these last because they're area-based labels (vs point-based, like for star names), and area-based labels have more freedom to move around. If you plot area-based labels first, then it would limit the available space for point-based labels.

        Args:
            style: Styling of the constellation labels. If None, then the plot's style (specified when creating the plot) will be used
            label_fn: Callable for determining the label for each constellation. The default function returns the constellation's name in uppercase.
            collision_handler: An instance of [CollisionHandler][starplot.CollisionHandler] that describes what to do on collisions with other labels, markers, etc. If `None`, then `CollisionHandler(allow_constellation_line_collisions=True)` will be used (**Important: this function does NOT default to the plot's collision handler, since it's the only area-based label function and collisions should be handled differently**).
        """

        collision_handler = collision_handler or CollisionHandler(
            allow_constellation_line_collisions=True
        )

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
            text = label_fn(constellation)

            self.text(
                text,
                centroid.x,
                centroid.y,
                style,
                area=constellation.boundary,  # TODO : make this intersection with clip path
                collision_handler=collision_handler,
                gid="constellations-label-name",
            )
