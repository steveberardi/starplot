from typing import Callable, Mapping
from functools import cache

import rtree
from skyfield.api import Star as SkyfieldStar

import numpy as np

from starplot import callables
from starplot.coordinates import CoordinateSystem
from starplot.data import bayer, stars, flamsteed
from starplot.data.stars import StarCatalog, STAR_NAMES
from starplot.models.star import Star, from_tuple
from starplot.styles import ObjectStyle, use_style
from starplot.profile import profile


class StarPlotterMixin:
    def _load_stars(self, catalog, filters=None):
        extent = self._extent_mask()

        return stars.load(
            extent=extent,
            catalog=catalog,
            filters=filters,
        )

    def _scatter_stars(self, ras, decs, sizes, alphas, colors, style=None, **kwargs):
        style = style or self.style.star
        edge_colors = kwargs.pop("edgecolors", None)

        if not edge_colors:
            if style.marker.edge_color:
                edge_colors = style.marker.edge_color.as_hex()
            else:
                edge_colors = "none"

        plotted = self.ax.scatter(
            ras,
            decs,
            s=sizes,
            c=colors,
            marker=kwargs.pop("symbol", None) or style.marker.symbol_matplot,
            zorder=kwargs.pop("zorder", None) or style.marker.zorder,
            edgecolors=edge_colors,
            alpha=alphas,
            gid="stars",
            **self._plot_kwargs(),
            **kwargs,
        )

        if self._background_clip_path is not None:
            plotted.set_clip_on(True)
            plotted.set_clip_path(self._background_clip_path)

        return plotted

    def _star_labels(
        self,
        star_objects: list[Star],
        star_sizes: list[float],
        label_row_ids: list,
        style: ObjectStyle,
        labels: Mapping[str, str],
        bayer_labels: bool,
        flamsteed_labels: bool,
        label_fn: Callable[[Star], str],
    ):
        _bayer = []
        _flamsteed = []

        # Plot all star common names first
        for i, s in enumerate(star_objects):
            if s._row_id not in label_row_ids:
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

            label = labels.get(s.hip) if label_fn is None else label_fn(s)
            bayer_desig = bayer.hip.get(s.hip)
            flamsteed_num = flamsteed.hip.get(s.hip)

            if label:
                self.text(
                    label,
                    s.ra,
                    s.dec,
                    style=style.label.offset_from_marker(
                        marker_symbol=style.marker.symbol,
                        marker_size=star_sizes[i],
                        scale=self.scale,
                    ),
                    hide_on_collision=self.hide_colliding_labels,
                    gid="stars-label-name",
                )

            if bayer_labels and bayer_desig:
                _bayer.append((bayer_desig, s.ra, s.dec, star_sizes[i], s.hip))

            if flamsteed_labels and flamsteed_num:
                _flamsteed.append((flamsteed_num, s.ra, s.dec, star_sizes[i], s.hip))

        # Plot bayer/flamsteed
        for bayer_desig, ra, dec, star_size, _ in _bayer:
            self.text(
                bayer_desig,
                ra,
                dec,
                style=self.style.bayer_labels.offset_from_marker(
                    marker_symbol=style.marker.symbol,
                    marker_size=star_size,
                    scale=self.scale,
                ),
                hide_on_collision=self.hide_colliding_labels,
                gid="stars-label-bayer",
            )

        for flamsteed_num, ra, dec, star_size, hip in _flamsteed:
            if hip in bayer.hip:
                continue
            self.text(
                flamsteed_num,
                ra,
                dec,
                style=self.style.flamsteed_labels.offset_from_marker(
                    marker_symbol=style.marker.symbol,
                    marker_size=star_size,
                    scale=self.scale,
                ),
                hide_on_collision=self.hide_colliding_labels,
                gid="stars-label-flamsteed",
            )

    def _prepare_star_coords(self, df):
        df["x"], df["y"] = (
            df["ra"],
            df["dec"],
        )
        return df

    @profile
    @use_style(ObjectStyle, "star")
    def stars(
        self,
        where: list = None,
        where_labels: list = None,
        catalog: StarCatalog = StarCatalog.HIPPARCOS,
        style: ObjectStyle = None,
        rasterize: bool = False,
        size_fn: Callable[[Star], float] = callables.size_by_magnitude,
        alpha_fn: Callable[[Star], float] = callables.alpha_by_magnitude,
        color_fn: Callable[[Star], str] = None,
        label_fn: Callable[[Star], str] = None,
        labels: Mapping[int, str] = STAR_NAMES,
        legend_label: str = "Star",
        bayer_labels: bool = False,
        flamsteed_labels: bool = False,
        *args,
        **kwargs,
    ):
        """
        Plots stars

        Args:
            where: A list of expressions that determine which stars to plot. See [Selecting Objects](/reference-selecting-objects/) for details.
            where_labels: A list of expressions that determine which stars are labeled on the plot. See [Selecting Objects](/reference-selecting-objects/) for details.
            catalog: The catalog of stars to use: "hipparcos", "big-sky-mag11", or "big-sky" -- see [`StarCatalog`](/reference-data/#starplot.data.stars.StarCatalog) for details
            style: If `None`, then the plot's style for stars will be used
            rasterize: If True, then the stars will be rasterized when plotted, which can speed up exporting to SVG and reduce the file size but with a loss of image quality
            size_fn: Callable for calculating the marker size of each star. If `None`, then the marker style's size will be used.
            alpha_fn: Callable for calculating the alpha value (aka "opacity") of each star. If `None`, then the marker style's alpha will be used.
            color_fn: Callable for calculating the color of each star. If `None`, then the marker style's color will be used.
            label_fn: Callable for determining the label of each star. If `None`, then the names in the `labels` kwarg will be used.
            labels: A dictionary that maps a star's HIP id to the label that'll be plotted for that star. If you want to hide name labels, then set this arg to `None`.
            legend_label: Label for stars in the legend. If `None`, then they will not be in the legend.
            bayer_labels: If True, then Bayer labels for stars will be plotted.
            flamsteed_labels: If True, then Flamsteed number labels for stars will be plotted.
        """

        # fallback to style if callables are None
        color_hex = (
            style.marker.color.as_hex()
        )  # calculate color hex once here to avoid repeated calls in color_fn()
        size_fn = size_fn or (lambda d: style.marker.size)
        alpha_fn = alpha_fn or (lambda d: style.marker.alpha)
        color_fn = color_fn or (lambda d: color_hex)

        where = where or []
        where_labels = where_labels or []
        stars_to_index = []

        labels = {} if labels is None else {**STAR_NAMES, **labels}

        star_results = self._load_stars(catalog, filters=where)
        
        star_results_labeled = star_results
        for f in where_labels:
            star_results_labeled = star_results_labeled.filter(f)
        
        label_row_ids = star_results_labeled.to_pandas()['rowid'].tolist()

        nearby_stars_df = star_results.to_pandas()

        nearby_stars = SkyfieldStar.from_dataframe(nearby_stars_df)
        astrometric = self.ephemeris["earth"].at(self.timescale).observe(nearby_stars)
        stars_ra, stars_dec, _ = astrometric.radec()
        nearby_stars_df["ra"], nearby_stars_df["dec"] = (
            stars_ra.hours * 15,
            stars_dec.degrees,
        )
        self._prepare_star_coords(nearby_stars_df)

        starz = []
        ctr = 0

        for star in nearby_stars_df.itertuples():
            obj = from_tuple(star)
            ctr += 1

            if self._coordinate_system == CoordinateSystem.RA_DEC:
                data_xy = self._proj.transform_point(star.ra, star.dec, self._crs)
            elif self._coordinate_system == CoordinateSystem.AZ_ALT:
                data_xy = self._proj.transform_point(star.x, star.y, self._crs)
            else:
                raise ValueError("Unrecognized coordinate system")

            display_x, display_y = self.ax.transData.transform(data_xy)

            if (
                display_x < 0
                or display_y < 0
                or np.isnan(display_x)
                or np.isnan(display_y)
                or self._is_clipped([(display_x, display_y)])
            ):
                continue

            size = size_fn(obj) * self.scale**2
            alpha = alpha_fn(obj)
            color = color_fn(obj) or style.marker.color.as_hex()

            if obj.magnitude < 5:
                # radius = ((size**0.5 / 2) / self.scale) #/ 3.14
                radius = size**0.5 / 5

                bbox = np.array(
                    (
                        display_x - radius,
                        display_y - radius,
                        display_x + radius,
                        display_y + radius,
                    )
                )
                # if obj.name == "Sirius":
                #     print(bbox)
                # if obj.name == "Electra":
                #     print(bbox)

                if self._stars_rtree.get_size() > 0:
                    self._stars_rtree.insert(
                        0,
                        bbox,
                        None,
                    )
                else:
                    # if the index has no stars yet, then wait until end to load for better performance
                    stars_to_index.append((ctr, bbox, None))

            starz.append((star.x, star.y, size, alpha, color, obj))

        starz.sort(key=lambda s: s[2], reverse=True)  # sort by descending size

        if not starz:
            self.logger.debug(f"Star count = {len(starz)}")
            return

        x, y, sizes, alphas, colors, star_objects = zip(*starz)

        self._objects.stars.extend(star_objects)

        self.logger.debug(f"Star count = {len(star_objects)}")

        # Plot Stars
        self._scatter_stars(
            x,
            y,
            sizes,
            alphas,
            colors,
            style=style,
            zorder=style.marker.zorder,
            edgecolors=style.marker.edge_color.as_hex()
            if style.marker.edge_color
            else "none",
            rasterized=rasterize,
        )

        self._add_legend_handle_marker(legend_label, style.marker)

        if stars_to_index:
            self._stars_rtree = rtree.index.Index(stars_to_index)

        if labels:
            self._star_labels(
                star_objects,
                sizes,
                label_row_ids,
                style,
                labels,
                bayer_labels,
                flamsteed_labels,
                label_fn,
            )
