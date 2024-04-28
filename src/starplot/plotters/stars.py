from typing import Callable, Mapping

import numpy as np

from skyfield.api import Star as SkyfieldStar

from starplot import callables
from starplot.data import bayer, stars
from starplot.data.stars import StarCatalog, STAR_NAMES
from starplot.models import Star
from starplot.styles import ObjectStyle, LabelStyle, use_style


class StarPlotterMixin:
    def _load_stars(self, catalog, limiting_magnitude=None):
        stardata = stars.load(catalog)

        ra_buffer = (self.ra_max - self.ra_min) / 4
        dec_buffer = (self.dec_max - self.dec_min) / 4

        if limiting_magnitude is not None:
            stardata = stardata[(stardata["magnitude"] <= limiting_magnitude)]

        stardata = stardata[
            (stardata["dec_degrees"] < self.dec_max + dec_buffer)
            & (stardata["dec_degrees"] > self.dec_min - dec_buffer)
        ]

        if self.ra_max <= 24 and self.ra_min >= 0:
            stardata = stardata[
                (stardata["ra_hours"] < self.ra_max + ra_buffer)
                & (stardata["ra_hours"] > self.ra_min - ra_buffer)
            ]
        elif self.ra_max > 24:
            # handle wrapping
            stardata = stardata[
                (stardata["ra_hours"] > self.ra_min - ra_buffer)
                | (stardata["ra_hours"] < self.ra_max - 24 + ra_buffer)
            ]
        elif self.ra_min < 0:
            stardata = stardata[
                (stardata["ra_hours"] > 24 + self.ra_min - ra_buffer)
                | (stardata["ra_hours"] < self.ra_max + ra_buffer)
            ]

        return stardata

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
        where_labels: list,
        style: LabelStyle,
        labels: Mapping[str, str],
        bayer_labels: bool,
    ):
        for s in star_objects:
            if where_labels and not all([e.evaluate(s) for e in where_labels]):
                continue

            name = labels.get(s.hip)
            bayer_desig = bayer.hip.get(s.hip)

            if name:
                self.text(name, s.ra, s.dec, style)

            if bayer_labels and bayer_desig:
                self.text(bayer_desig, s.ra, s.dec, self.style.bayer_labels)

    def _prepare_star_coords(self, df):
        df["x"], df["y"] = (
            df["ra"],
            df["dec"],
        )
        return df

    @use_style(ObjectStyle, "star")
    def stars(
        self,
        mag: float = 6.0,
        catalog: StarCatalog = StarCatalog.HIPPARCOS,
        style: ObjectStyle = None,
        rasterize: bool = False,
        size_fn: Callable[[Star], float] = callables.size_by_magnitude,
        alpha_fn: Callable[[Star], float] = callables.alpha_by_magnitude,
        color_fn: Callable[[Star], str] = None,
        where: list = None,
        where_labels: list = None,
        labels: Mapping[int, str] = STAR_NAMES,
        legend_label: str = "Star",
        bayer_labels: bool = False,
        *args,
        **kwargs,
    ):
        """
        Plots stars

        Args:
            mag: Limiting magnitude of stars to plot. For more control of what stars to plot, use the `where` kwarg. **Note:** if you pass `mag` and `where` then `mag` will be ignored
            catalog: The catalog of stars to use: "hipparcos" or "tycho-1" -- Hipparcos is the default and has about 10x less stars than Tycho-1 but will also plot much faster
            style: If `None`, then the plot's style for stars will be used
            rasterize: If True, then the stars will be rasterized when plotted, which can speed up exporting to SVG and reduce the file size but with a loss of image quality
            size_fn: Callable for calculating the marker size of each star. If `None`, then the marker style's size will be used.
            alpha_fn: Callable for calculating the alpha value (aka "opacity") of each star. If `None`, then the marker style's alpha will be used.
            color_fn: Callable for calculating the color of each star. If `None`, then the marker style's color will be used.
            where: A list of expressions that determine which stars to plot. See [Selecting Objects](/reference-selecting-objects/) for details.
            where_labels: A list of expressions that determine which stars are labeled on the plot. See [Selecting Objects](/reference-selecting-objects/) for details.
            labels: A dictionary that maps a star's HIP id to the label that'll be plotted for that star. If you want to hide name labels, then set this arg to `None`.
            legend_label: Label for stars in the legend. If `None`, then they will not be in the legend.
            bayer_labels: If True, then Bayer labels for stars will be plotted. Set this to False if you want to hide Bayer labels.
        """
        self.logger.debug("Plotting stars...")

        # fallback to style if callables are None
        size_fn = size_fn or (lambda d: style.marker.size)
        alpha_fn = alpha_fn or (lambda d: style.marker.alpha)
        color_fn = color_fn or (lambda d: style.marker.color.as_hex())

        where = where or []

        if where:
            mag = None

        if labels is None:
            labels = {}
        else:
            labels = {**STAR_NAMES, **labels}

        star_size_multiplier = self._size_multiplier * style.marker.size / 5

        nearby_stars_df = self._load_stars(catalog, mag)
        nearby_stars = SkyfieldStar.from_dataframe(nearby_stars_df)
        astrometric = self.ephemeris["earth"].at(self.timescale).observe(nearby_stars)
        stars_ra, stars_dec, _ = astrometric.radec()
        nearby_stars_df["ra"], nearby_stars_df["dec"] = (
            stars_ra.hours * 15,
            stars_dec.degrees,
        )
        self._prepare_star_coords(nearby_stars_df)

        starz = []

        for star in nearby_stars_df.itertuples():
            m = star.magnitude
            ra, dec = star.ra, star.dec
            hip_id = star.Index

            obj = Star(ra=ra / 15, dec=dec, magnitude=m, bv=star.bv)

            if np.isfinite(hip_id):
                obj.hip = hip_id
                obj.name = STAR_NAMES.get(hip_id)

            if not all([e.evaluate(obj) for e in where]):
                continue

            size = size_fn(obj) * star_size_multiplier
            alpha = alpha_fn(obj)
            color = color_fn(obj) or style.marker.color.as_hex()

            starz.append((star.x, star.y, size, alpha, color, obj))

        starz.sort(key=lambda s: s[2], reverse=True)  # sort by descending size

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
            edgecolors=self.style.background_color.as_hex(),
            rasterized=rasterize,
        )

        self._add_legend_handle_marker(legend_label, style.marker)

        self._star_labels(star_objects, where_labels, style.label, labels, bayer_labels)
