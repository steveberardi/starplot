from typing import Callable, Mapping

from skyfield.api import Star as SkyfieldStar

from starplot import callables
from starplot.data import bayer, stars
from starplot.data.stars import StarCatalog, STAR_NAMES
from starplot.models import Star
from starplot.styles import ObjectStyle, LabelStyle, use_style


class StarPlotterMixin:
    def _load_stars(self, catalog, limiting_magnitude):
        stardata = stars.load(catalog)

        ra_buffer = (self.ra_max - self.ra_min) / 4
        dec_buffer = (self.dec_max - self.dec_min) / 4

        stardata = stardata[
            (stardata["magnitude"] <= limiting_magnitude)
            & (stardata["dec_degrees"] < self.dec_max + dec_buffer)
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

    def _scatter_stars(
        self, ras, decs, sizes, alphas, colors, style=None, epoch_year=None, **kwargs
    ):
        style = style or self.style.star
        edge_colors = kwargs.pop("edgecolors", None)

        if not edge_colors:
            if style.marker.edge_color:
                edge_colors = style.marker.edge_color.as_hex()
            else:
                edge_colors = "none"

        return self.ax.scatter(
            ras,
            decs,
            sizes,
            colors,
            marker=kwargs.pop("symbol", None) or style.marker.symbol_matplot,
            zorder=kwargs.pop("zorder", None) or style.marker.zorder,
            edgecolors=edge_colors,
            alpha=alphas,
            **self._plot_kwargs(),
            **kwargs,
        )

    def _star_labels(
        self,
        stars_df,
        mag: float,
        style: LabelStyle,
        labels: Mapping[str, str],
        bayer_labels: bool,
    ):
        stars_df = stars_df[(stars_df["magnitude"] <= mag)]
        stars_df.sort_values("magnitude")

        for hip_id, s in stars_df.iterrows():
            name = labels.get(hip_id)
            bayer_desig = bayer.hip.get(hip_id)
            ra, dec = s["ra_hours"], s["dec_degrees"]

            if name:
                self._plot_text(
                    ra,
                    dec,
                    name,
                    ha="left",
                    va="top",
                    **style.matplot_kwargs(self._size_multiplier),
                )

            if bayer_labels and bayer_desig:
                self._plot_text(
                    ra,
                    dec,
                    bayer_desig,
                    ha="right",
                    va="bottom",
                    **self.style.bayer_labels.matplot_kwargs(self._size_multiplier),
                )

    @use_style(ObjectStyle, "star")
    def stars(
        self,
        mag: float = 6.0,
        mag_labels: float = 6.0,
        catalog: StarCatalog = StarCatalog.HIPPARCOS,
        style: ObjectStyle = None,
        rasterize: bool = False,
        size_fn: Callable[[Star], float] = callables.size_by_magnitude,
        alpha_fn: Callable[[Star], float] = callables.alpha_by_magnitude,
        color_fn: Callable[[Star], str] = None,
        visible_fn: Callable[[Star], bool] = None,
        labels: Mapping[int, str] = STAR_NAMES,
        legend_label: str = "Star",
        bayer_labels: bool = False,
        *args,
        **kwargs,
    ):
        """
        Plots stars

        Args:
            mag: Limiting magnitude of stars to plot
            mag_labels: Limiting magnitude of stars to label on the plot
            catalog: The catalog of stars to use: "hipparcos" or "tycho-1" -- Hipparcos is the default and has about 10x less stars than Tycho-1 but will also plot much faster
            style: If `None`, then the plot's style for stars will be used
            rasterize: If True, then the stars will be rasterized when plotted, which can speed up exporting to SVG and reduce the file size but with a loss of image quality
            size_fn: Callable for calculating the marker size of each star. If `None`, then the marker style's size will be used.
            alpha_fn: Callable for calculating the alpha value (aka "opacity") of each star. If `None`, then the marker style's alpha will be used.
            color_fn: Callable for calculating the color of each star. If `None`, then the marker style's color will be used.
            visible_fn: A callable that determines if a star should be plotted. Receives an instance of the star and should return True to plot the star, return False to hide it. Note: this callable is called *after* filtering stars by magnitude. If None (the default), then the stars will not be filtered by this callable.
            labels: A dictionary that maps a star's HIP id to the label that'll be plotted for that star. If you want to hide name labels, then set this arg to `None`.
            legend_label: Label for stars in the legend. If `None`, then they will not be in the legend.
            bayer_labels: If True, then Bayer labels for stars will be plotted. Set this to False if you want to hide Bayer labels.
        """
        self.logger.debug("Plotting stars...")

        # fallback to style if callables are None
        size_fn = size_fn or (lambda d: style.marker.size)
        alpha_fn = alpha_fn or (lambda d: style.marker.alpha)
        color_fn = color_fn or (lambda d: style.marker.color.as_hex())

        visible_fn = visible_fn or (lambda d: True)

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
        epoch_year = nearby_stars_df.iloc[0]["epoch_year"]

        starz = []

        # TODO : transform points first, find in-axis stars, 
        # then iterate again and calc size/alpha/color etc

        for _, star in nearby_stars_df.iterrows():
            m = star.magnitude
            ra, dec = star.ra, star.dec

            obj = Star(ra=ra/15, dec=dec, magnitude=m, bv=star.get("bv"))

            if not visible_fn(obj):
                continue

            size = size_fn(obj) * star_size_multiplier
            alpha = alpha_fn(obj)
            color = color_fn(obj) or style.marker.color.as_hex()

            starz.append((ra, dec, size, alpha, color, obj))

        starz.sort(key=lambda s: s[2], reverse=True)  # sort by descending size

        ras, decs, sizes, alphas, colors, star_objects = zip(*starz)

        # much more efficient!
        # TODO : move to function
        import numpy as np
        radec_projected = self._proj.transform_points(self._crs, np.array(ras), np.array(decs))
        data_to_axes = self.ax.transData + self.ax.transAxes.inverted()
        x, y, _ = zip(*radec_projected)
        ax_coords = data_to_axes.transform((x,y))

        for i, (ax, ay) in enumerate(ax_coords):
            if 0 < ax < 1 and 0 < ay < 1:
                self.objects.stars.append(star_objects[i])

        # Plot Stars
        self._scatter_stars(
            ras,
            decs,
            sizes,
            alphas,
            colors,
            style=style,
            zorder=style.marker.zorder,
            edgecolors=self.style.background_color.as_hex(),
            rasterized=rasterize,
            epoch_year=epoch_year,
        )

        self._add_legend_handle_marker(legend_label, style.marker)

        self._star_labels(
            nearby_stars_df, mag_labels, style.label, labels, bayer_labels
        )
