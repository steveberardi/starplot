from collections.abc import Callable
from pathlib import Path

import numpy as np
import rtree
from ibis import _ as ibis_table
from skyfield.api import Star as SkyfieldStar

from starplot.callables import size_by_magnitude
from starplot.data import stars
from starplot.data.catalogs import BIG_SKY_MAG11, Catalog
from starplot.data.translations import translate
from starplot.models.star import Star, from_tuple
from starplot.plotters.text import CollisionHandler
from starplot.profile import profile
from starplot.styles import GradientStyle, ObjectStyle, use_style
from starplot.utils import normalize_where


class StarPlotterMixin:
    def _load_stars(self, catalog, filters=None, sql=None):
        extent = self._extent_mask()

        return stars.load(
            extent=extent,
            catalog=catalog,
            filters=filters,
            sql=sql,
        )

    def _scatter_stars(self, ras, decs, sizes, opacity_values, colors, style, gid):
        style = style or self.style.star

        self.canvas.markers(
            xs=np.array(ras),
            ys=np.array(decs),
            style=style.marker,
            gid=gid,
            sizes=sizes,
            colors=colors,
            opacity_values=opacity_values,
        )

    def _star_labels(
        self,
        star_objects: list[Star],
        star_sizes: list[float],
        label_pks: list,
        style: ObjectStyle,
        bayer_labels: bool,
        flamsteed_labels: bool,
        label_fn: Callable[[Star], str],
        collision_handler: CollisionHandler,
    ):
        _bayer = []
        _flamsteed = []

        # Plot all star common names first
        for i, s in enumerate(star_objects):
            if s.pk not in label_pks:
                continue

            if (
                s.hip
                and s.hip in self._labeled_stars
                or s.tyc
                and s.tyc in self._labeled_stars
            ):
                continue
            elif s.hip:
                self._labeled_stars.append(s.hip)
            elif s.tyc:
                self._labeled_stars.append(s.tyc)

            label = label_fn(s)
            bayer_desig = s.bayer
            flamsteed_num = s.flamsteed

            if label:
                self.text(
                    label,
                    s.ra,
                    s.dec,
                    style=self._offset_from_marker(
                        style=style.label,
                        text=label,
                        marker_size=star_sizes[i],
                    ),
                    collision_handler=collision_handler,
                    gid="stars-label-name",
                )

            if bayer_labels and bayer_desig and s.is_primary:
                _bayer.append((bayer_desig, s.ra, s.dec, star_sizes[i]))

            if flamsteed_labels and flamsteed_num and not bayer_desig and s.is_primary:
                _flamsteed.append((flamsteed_num, s.ra, s.dec, star_sizes[i]))

        # Plot bayer/flamsteed
        for bayer_desig, ra, dec, star_size in _bayer:
            self.text(
                bayer_desig,
                ra,
                dec,
                style=self._offset_from_marker(
                    style=self.style.bayer_labels,
                    text=bayer_desig,
                    marker_size=star_size,
                ),
                collision_handler=collision_handler,
                gid="stars-label-bayer",
            )

        for flamsteed_num, ra, dec, star_size in _flamsteed:
            self.text(
                flamsteed_num,
                ra,
                dec,
                style=self._offset_from_marker(
                    style=self.style.flamsteed_labels,
                    text=str(flamsteed_num),
                    marker_size=star_size,
                ),
                collision_handler=collision_handler,
                gid="stars-label-flamsteed",
            )

    def _prepare_star_coords(self, df, limit_by_altaz=False):
        df["x"], df["y"] = (
            df["ra"],
            df["dec"],
        )
        return df

    @profile
    @use_style(ObjectStyle, "star")
    def stars(
        self,
        where: list | None = None,
        where_labels: list | bool | None = None,
        catalog: Catalog | Path | str = BIG_SKY_MAG11,
        style: ObjectStyle = None,
        size_fn: Callable[[Star], float] = size_by_magnitude,
        opacity_fn: Callable[[Star], float] | None = None,
        color_fn: Callable[[Star], str | GradientStyle] | None = None,
        label_fn: Callable[[Star], str] = Star.get_label,
        legend_label: str = "Star",
        bayer_labels: bool = False,
        flamsteed_labels: bool = False,
        sql: str | None = None,
        sql_labels: str | None = None,
        collision_handler: CollisionHandler = None,
        gid_markers: str = "stars",
        gid_labels: str = "stars-labels",
    ):
        """
        Plots stars

        Args:
            where: A list of expressions that determine which stars to plot. See [Selecting Objects](/reference-selecting-objects/) for details.
            where_labels: A list of expressions that determine which stars are labeled on the plot (this includes all labels: name, Bayer, and Flamsteed). Can also be a boolean: if `False` then no labels will be plotted.. See [Selecting Objects](/reference-selecting-objects/) for details.
            catalog: The catalog of stars to use -- see [catalogs overview](/data/overview/) for details
            style: If `None`, then the plot's style for stars will be used
            size_fn: Callable for calculating the marker size of each star. If `None`, then the marker style's size will be used.
            opacity_fn: Callable for calculating the opacity value of each star. If `None`, then the marker style's opacity will be used.
            color_fn: Callable for calculating the color of each star. If `None`, then the marker style's color will be used.
            label_fn: Callable for determining the label of each star.
            legend_label: Label for stars in the legend. If `None`, then they will not be in the legend.
            bayer_labels: If True, then Bayer labels for stars will be plotted.
            flamsteed_labels: If True, then Flamsteed number labels for stars will be plotted.
            sql: SQL query for selecting stars (table name is `_`). This query will be applied _after_ any filters in the `where` kwarg.
            sql_labels: SQL query for selecting stars that will be labeled (table name is `_`). Applied _after_ any filters in the `where_labels` kwarg.
            collision_handler: An instance of [CollisionHandler][starplot.CollisionHandler] that describes what to do on label collisions with other labels, markers, etc. If `None`, then the collision handler of the plot will be used.
            gid_markers: Group id for the markers in the exported SVG
            gid_labels: Group id for the labels in the exported SVG

        """

        # fallback to style if callables are None
        size_fn = size_fn or (lambda d: style.marker.size)
        opacity_fn = opacity_fn or (lambda d: style.marker.opacity)
        color_fn = color_fn or (lambda d: style.marker.fill)

        self._last_used_size_fn = size_fn

        handler = collision_handler or self.point_label_handler
        where = normalize_where(where)
        where_labels = normalize_where(where_labels)
        stars_to_index = []

        star_results = self._load_stars(catalog, filters=where, sql=sql)

        star_results_labeled = star_results
        for f in where_labels:
            star_results_labeled = star_results_labeled.filter(f)

        if sql_labels:
            result = (
                star_results_labeled.alias("_").sql(sql_labels).select("pk").execute()
            )
            pks = result["pk"].to_list()
            star_results_labeled = star_results_labeled.filter(ibis_table.pk.isin(pks))

        label_pks = star_results_labeled.to_pandas()["pk"].tolist()

        stars_df = star_results.to_pandas()
        stars_df["ra_hours"], stars_df["dec_degrees"] = (stars_df.ra / 15, stars_df.dec)

        nearby_stars = SkyfieldStar.from_dataframe(stars_df)
        astrometric = self.earth.at(self.observer.timescale).observe(nearby_stars)
        stars_ra, stars_dec, _ = astrometric.radec()
        stars_df["ra"], stars_df["dec"] = (
            stars_ra.hours * 15,
            stars_dec.degrees,
        )
        stars_df = self._prepare_star_coords(stars_df)

        starz = []
        rtree_id = 1

        stars_df["display_x"], stars_df["display_y"] = self.canvas._to_display(
            stars_df["x"].to_numpy(),
            stars_df["y"].to_numpy(),
        )
        stars_df = stars_df[(stars_df["display_x"] >= 0) & (stars_df["display_y"] >= 0)]

        for star in stars_df.itertuples():
            display_x, display_y = star.display_x, star.display_y

            obj = from_tuple(star)
            size = size_fn(obj) * self.scale
            opacity = opacity_fn(obj)
            color = color_fn(obj) or style.marker.fill

            if size > 10:
                rtree_id += 1
                radius = size / 2.5
                bbox = np.array(
                    (
                        display_x - radius,
                        display_y - radius,
                        display_x + radius,
                        display_y + radius,
                    )
                )
                if self.debug_text:
                    self._debug_bbox(bbox, color="#39FF14", width=1)
                if self._stars_rtree.get_size() > 0:
                    self._stars_rtree.insert(
                        0,
                        bbox,
                        None,
                    )
                else:
                    # if the index has no stars yet, then wait until end to load for better performance
                    stars_to_index.append((rtree_id, bbox, None))

            starz.append((star.x, star.y, size, opacity, color, obj))

        starz.sort(key=lambda s: s[2], reverse=True)  # sort by descending size

        if not starz:
            self.logger.debug("No stars found.")
            return

        x, y, sizes, opacity_values, colors, star_objects = zip(*starz)

        self._objects.stars.extend(star_objects)

        self.logger.debug(f"Star count = {len(star_objects)}")

        self._scatter_stars(
            x,
            y,
            sizes,
            opacity_values,
            colors,
            style=style,
            gid=gid_markers,
        )

        _legend_label = translate(legend_label, self.language) or legend_label
        self._add_legend_handle_marker(_legend_label, style.marker)

        if stars_to_index:
            self._stars_rtree = rtree.index.Index(stars_to_index)

        with self.canvas.group(gid=gid_labels):
            self._star_labels(
                star_objects,
                sizes,
                label_pks,
                style,
                bayer_labels,
                flamsteed_labels,
                label_fn,
                handler,
            )
