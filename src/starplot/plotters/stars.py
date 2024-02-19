import math

from typing import Callable

from skyfield.api import Star

from starplot import callables
from starplot.data import bayer, stars
from starplot.models import SimpleObject
from starplot.styles import MarkerStyle


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

        if self.ra_max < 24 and self.ra_min > 0:
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

    def _plot_star_labels(self, stars_df, limiting_magnitude_labels, style):
        stars_df = stars_df[(stars_df["magnitude"] <= limiting_magnitude_labels)]

        stars_df.sort_values("magnitude")

        for hip_id, s in stars_df.iterrows():
            name = stars.hip_names.get(hip_id)
            bayer_desig = bayer.hip.get(hip_id)
            ra, dec = s["ra_hours"], s["dec_degrees"]

            if name and style.label.visible:
                self._plot_text(
                    ra - 0.01,
                    dec - 0.12,
                    name,
                    ha="left",
                    va="top",
                    **style.label.matplot_kwargs(self._size_multiplier),
                )

            if bayer_desig and self.style.bayer_labels.visible:
                self._plot_text(
                    ra + 0.01,
                    dec,
                    bayer_desig,
                    ha="right",
                    va="bottom",
                    **self.style.bayer_labels.matplot_kwargs(self._size_multiplier),
                )

    def plot_stars(
        self,
        limiting_magnitude: float = 6.0,
        limiting_magnitude_labels: float = 6.0,
        catalog: stars.StarCatalog = stars.StarCatalog.HIPPARCOS,
        style: MarkerStyle = None,
        rasterize: bool = False,
        separation_tolerance: float = 60 / 3600,
        size_fn: Callable[[SimpleObject], float] = callables.size_by_magnitude,
        alpha_fn: Callable[[SimpleObject], float] = callables.alpha_by_magnitude,
        color_fn: Callable[[SimpleObject], float] = None,
        *args,
        **kwargs,
    ):
        """
        Plots stars

        Args:
            limiting_magnitude: Limiting magnitude of stars to plot
            limiting_magnitude_labels: Limiting magnitude of stars to label on the plot
            catalog: The catalog of stars to use: "hipparcos" or "tycho-1" -- Hipparcos is the default and has about 10x less stars than Tycho-1 but will also plot much faster
            style: If `None`, then the plot's style for stars will be used
            rasterize: If True, then the stars will be rasterized when plotted, which can speed up exporting to SVG and reduce the file size but with a loss of image quality
            separation_tolerance: Tolerance for determining if nearby stars should be plotted with separate z-orders (to prevent them from overlapping)
            size_fn: Callable for calculating the marker size of each star. If `None`, then the marker style's size will be used.
            alpha_fn: Callable for calculating the alpha value (aka "opacity") of each star. If `None`, then the marker style's alpha will be used.
            color_fn: Callable for calculating the color of each star. If `None`, then the marker style's color will be used.

        """
        self.logger.debug("Plotting stars...")

        style = style or self.style.star
        color_fn = color_fn or (lambda d: style.marker.color.as_hex())
        earth = self.ephemeris["earth"]

        # More pixels/RA means less buckets
        ra_size = (self.ra_max - self.ra_min) * 15
        dec_size = self.dec_max - self.dec_min
        area = ra_size * dec_size
        pixels_per_radec = math.sqrt(self.resolution**2 / area)
        num_buckets = (1 / pixels_per_radec) * 1_000
        buckets = {}
        buckets_deferred = {}

        def calc_bucket(ra, dec):
            extent_ra = self.ra_max - self.ra_min
            extent_dec = self.dec_max - self.dec_min

            b_ra = (ra - self.ra_min) / extent_ra * num_buckets
            b_dec = (dec - self.dec_min) / extent_dec * num_buckets

            if round(b_ra) > b_ra:
                nn_ra = b_ra + 1
            else:
                nn_ra = b_ra - 1

            if round(b_dec) > b_dec:
                nn_dec = b_dec + 1
            else:
                nn_dec = b_dec - 1

            return (int(b_ra), int(b_dec)), (int(nn_ra), int(nn_dec))

        nearby_stars_df = self._load_stars(catalog, limiting_magnitude)
        nearby_stars = Star.from_dataframe(nearby_stars_df)
        astrometric = earth.at(self.timescale).observe(nearby_stars)
        stars_ra, stars_dec, _ = astrometric.radec()
        nearby_stars_df["ra"], nearby_stars_df["dec"] = (
            stars_ra.hours * 15,
            stars_dec.degrees,
        )
        epoch_year = nearby_stars_df.iloc[0]["epoch_year"]

        sizes = []
        alphas = []
        colors = []
        biggest_bucket_size = 0

        close_nn = 0
        idx = 0

        for _, star in nearby_stars_df.iterrows():
            m = star.magnitude
            ra, dec = star.ra, star.dec
            b, nn = calc_bucket(ra, dec)

            obj = SimpleObject(ra=ra, dec=dec, magnitude=m, bv=star.get("bv"))
            size = size_fn(obj) * self._star_size_multiplier
            alpha = alpha_fn(obj)
            color = color_fn(obj) or style.marker.color.as_hex()

            size_px = math.sqrt(size * self.pixels_per_point)  # marker size in pixels
            rep = (idx, ra, dec, size, alpha, color, size_px)

            if b not in buckets:
                buckets[b] = [rep]

            else:
                indices, _, _, sizes, _, _, sizes_px = zip(*buckets[b])
                seps_degrees = [
                    astrometric[idx].separation_from(astrometric[i]).degrees
                    for i in indices
                ]

                if buckets.get(nn):
                    nn_indices, _, _, nn_sizes, _, _, nn_sizes_px = zip(*buckets[nn])
                    nn_seps_degrees = [
                        astrometric[idx].separation_from(astrometric[i]).degrees
                        for i in nn_indices
                    ]
                    close_to_neighbor = min(nn_seps_degrees) < separation_tolerance * 4
                else:
                    close_to_neighbor = False

                if close_to_neighbor:
                    close_nn += 1
                # figure out if we need to defer this star
                # based on:
                #   min separation
                #   size of biggest
                #   size of bucket (pixels)

                if min(seps_degrees) < separation_tolerance * 4 and size_px > max(
                    sizes_px
                ):
                    # ensure the biggest star is always plotted first
                    buckets_deferred[b] = [s for s in buckets[b]]
                    buckets[b] = [rep]

                elif (
                    min(seps_degrees) > separation_tolerance * 10
                    and not close_to_neighbor
                ):
                    # if the star is small and stars in the bucket are small then just put it in base bucket
                    buckets[b].append(rep)

                elif b in buckets_deferred:
                    buckets_deferred[b].append(rep)
                    biggest_bucket_size = max(
                        biggest_bucket_size, len(buckets_deferred[b])
                    )

                else:
                    buckets_deferred[b] = [rep]
                    biggest_bucket_size = max(biggest_bucket_size, 1)

            idx += 1

        _, ra, dec, sizes, alphas, colors, _ = zip(*sum(buckets.values(), []))

        # self.logger.debug(
        #     f"Deferred Stars: {len(buckets_deferred.keys())} | NN: {close_nn}"
        # )

        # Plot Stars
        if style.marker.visible:
            self._scatter_stars(
                ra,
                dec,
                sizes,
                alphas,
                colors,
                style=style,
                rasterized=rasterize,
                epoch_year=epoch_year,
            )
            self._add_legend_handle_marker("Star", style.marker)

        # Plot deferred stars
        for idx in range(biggest_bucket_size):
            bucket_stars = []
            for b in buckets_deferred.values():
                if idx < len(b):
                    bucket_stars.append(b[idx])

            if not bucket_stars:
                continue

            _, ra, dec, sizes, alphas, colors, _ = zip(*bucket_stars)
            zorder = style.marker.zorder + (idx + 1) * 5
            edgecolors = self.style.background_color.as_hex()
            self._scatter_stars(
                ra,
                dec,
                sizes,
                alphas,
                colors,
                style=style,
                zorder=zorder,
                edgecolors=edgecolors,
                rasterized=rasterize,
                epoch_year=epoch_year,
            )

        self._plot_star_labels(nearby_stars_df, limiting_magnitude_labels, style)
