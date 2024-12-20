import geopandas as gpd
import numpy as np

from starplot.coordinates import CoordinateSystem
from starplot.data import DataFiles, constellations as condata, stars
from starplot.data.constellations import CONSTELLATIONS_FULL_NAMES
from starplot.models.constellation import from_tuple as constellation_from_tuple
from starplot.projections import Projection
from starplot.styles import PathStyle
from starplot.styles.helpers import use_style
from starplot.utils import points_on_line


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

        self._plot_constellation_labels(style.label, labels)

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
