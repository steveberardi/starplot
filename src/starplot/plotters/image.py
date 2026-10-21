import base64
import io
from pathlib import Path

import numpy as np
from PIL import Image
from skyfield.api import Star as SkyfieldStar

from starplot.coordinates import CoordinateSystem
from starplot.profile import profile
from starplot.styles import ImageStyle
from starplot.styles.helpers import use_style

# Rows resampled at a time, to bound memory use on large plots
CHUNK_ROWS = 256

# Points per edge when tracing the image's outline to find where it lands on the plot
OUTLINE_POINTS = 50


class PixelSkyModel:
    """
    Affine mapping between image pixels and the tangent plane at the center of the control points.
    """

    def __init__(self, control_points):
        if len(control_points) < 3:
            raise ValueError("At least 3 control points are required")

        pixels = np.array([p for p, _ in control_points], dtype=float)
        sky = np.array([s for _, s in control_points], dtype=float)

        # Fitting on the tangent plane at the mean position keeps the fit accurate across
        # large fields and near the RA wraparound or poles.
        ra_rad = np.radians(sky[:, 0])
        self.ra0 = (
            np.degrees(np.arctan2(np.sin(ra_rad).mean(), np.cos(ra_rad).mean())) % 360
        )
        self.dec0 = sky[:, 1].mean()

        xi, eta, valid = self._gnomonic(sky[:, 0], sky[:, 1], self.ra0, self.dec0)
        if not valid.all():
            raise ValueError("Control points must be within 90 degrees of each other")

        # The tangent-plane spread of the points must be 2D, otherwise the fit is degenerate
        spread = np.linalg.svd(
            np.column_stack([xi - xi.mean(), eta - eta.mean()]), compute_uv=False
        )
        if spread[1] < 1e-3 * spread[0]:
            raise ValueError("Control points must not all lie on a single line")

        design = np.column_stack([xi, eta, np.ones(len(xi))])

        # pixel = [xi, eta, 1] @ coeffs
        self.coeffs, *_ = np.linalg.lstsq(design, pixels, rcond=None)

        linear = self.coeffs[:2].T
        self._linear_inv = np.linalg.inv(linear)
        self._offset = self.coeffs[2]

    def _gnomonic(self, ra, dec, ra0, dec0):
        """Projects sky coordinates (degrees) onto the tangent plane at (ra0, dec0). Returns (xi, eta, valid) in radians."""
        ra, dec = np.radians(ra), np.radians(dec)
        ra0, dec0 = np.radians(ra0), np.radians(dec0)
        dra = ra - ra0

        cos_c = np.sin(dec0) * np.sin(dec) + np.cos(dec0) * np.cos(dec) * np.cos(dra)
        valid = cos_c > 1e-6
        cos_c = np.where(valid, cos_c, np.nan)

        xi = np.cos(dec) * np.sin(dra) / cos_c
        eta = (
            np.cos(dec0) * np.sin(dec) - np.sin(dec0) * np.cos(dec) * np.cos(dra)
        ) / (cos_c)
        return xi, eta, valid

    def _inverse_gnomonic(self, xi, eta, ra0, dec0):
        """Inverse of `_gnomonic`. Returns (ra, dec) in degrees."""
        ra0, dec0 = np.radians(ra0), np.radians(dec0)
        rho = np.hypot(xi, eta)
        c = np.arctan(rho)
        sin_c, cos_c = np.sin(c), np.cos(c)

        # rho == 0 is the tangent point itself, where the ratios below are 0/0
        safe_rho = np.where(rho == 0, 1, rho)
        dec = np.arcsin(cos_c * np.sin(dec0) + eta * sin_c * np.cos(dec0) / safe_rho)
        dra = np.arctan2(
            xi * sin_c, rho * np.cos(dec0) * cos_c - eta * np.sin(dec0) * sin_c
        )
        return np.degrees(ra0 + dra) % 360, np.degrees(dec)

    def sky_to_pixel(self, ra, dec):
        """Returns (px, py, valid) for sky coordinates in degrees."""
        xi, eta, valid = self._gnomonic(ra, dec, self.ra0, self.dec0)
        px = xi * self.coeffs[0, 0] + eta * self.coeffs[1, 0] + self.coeffs[2, 0]
        py = xi * self.coeffs[0, 1] + eta * self.coeffs[1, 1] + self.coeffs[2, 1]
        return px, py, valid

    def pixel_to_sky(self, px, py):
        """Returns (ra, dec) in degrees for pixel coordinates."""
        xi = self._linear_inv[0, 0] * (px - self._offset[0]) + self._linear_inv[
            0, 1
        ] * (py - self._offset[1])
        eta = self._linear_inv[1, 0] * (px - self._offset[0]) + self._linear_inv[
            1, 1
        ] * (py - self._offset[1])
        return self._inverse_gnomonic(xi, eta, self.ra0, self.dec0)


def _sample_bilinear(pixels: np.ndarray, px, py) -> np.ndarray:
    height, width = pixels.shape[:2]
    x0, y0 = np.floor(px).astype(int), np.floor(py).astype(int)
    fx, fy = (px - x0)[:, None], (py - y0)[:, None]
    x0c, x1c = np.clip(x0, 0, width - 1), np.clip(x0 + 1, 0, width - 1)
    y0c, y1c = np.clip(y0, 0, height - 1), np.clip(y0 + 1, 0, height - 1)

    return (
        pixels[y0c, x0c] * (1 - fx) * (1 - fy)
        + pixels[y0c, x1c] * fx * (1 - fy)
        + pixels[y1c, x0c] * (1 - fx) * fy
        + pixels[y1c, x1c] * fx * fy
    )


class ImagePlotterMixin:
    def _data_to_radec(self, x, y):
        """Inverse of `_prepare_coords`: converts the plot's data coordinates to RA/DEC (degrees)"""
        if getattr(self, "_coordinate_system", None) != CoordinateSystem.AZ_ALT:
            return x, y

        finite = np.isfinite(x) & np.isfinite(y)
        az = np.where(finite, x, 0)
        apparent_alt = np.where(finite, y, 0)
        alt = apparent_alt

        def radec(alt):
            return self.observer.radec(az, alt, self.ephemeris_name)

        # Plotted altitudes include atmospheric refraction, which Observer.radec() doesn't account for,
        # so nudge the altitude until the star would be plotted where we started
        for _ in range(2):
            ra, dec = radec(alt)
            _, plotted_alt = self.observer._apparent(
                SkyfieldStar(ra_hours=ra / 15, dec_degrees=dec), self.ephemeris_name
            )
            alt = alt + (apparent_alt - plotted_alt)

        ra, dec = radec(alt)
        return np.where(finite, ra, np.nan), np.where(finite, dec, np.nan)

    @profile
    @use_style(ImageStyle, "image")
    def image(
        self,
        image: str | Path | Image.Image,
        control_points: list[tuple[tuple[float, float], tuple[float, float]]],
        style: ImageStyle = None,
        gid: str = "image",
    ):
        """
        Overlays an image on the plot, positioned by control points that map pixels in the image to coordinates in the sky.

        The image is transformed to fit the plot's projection, so it will line up with the stars and other objects on the plot.

        Args:
            image: Path to an image file, or a Pillow `Image`
            control_points: At least 3 pairs of points in the format `((x, y), (ra, dec))`, where `(x, y)` is a pixel in the image (origin at the top-left pixel, x increasing right, y increasing down) and `(ra, dec)` is its position in the sky, in degrees. Points should be spread out across the image, and they can't all lie on one line.
            style: Styling of the image. If None, then the plot's style (specified when creating the plot) will be used
            gid: Group id for this layer in the exported SVG
        """
        model = PixelSkyModel(control_points)

        if not isinstance(image, Image.Image):
            image = Image.open(image)
        source = np.asarray(image.convert("RGBA"))
        src_height, src_width = source.shape[:2]

        # Trace the image's outline onto the plot to find the region of the plot to resample
        right_edge, bottom_edge = src_width - 0.5, src_height - 0.5
        xs = np.linspace(-0.5, right_edge, OUTLINE_POINTS)
        ys = np.linspace(-0.5, bottom_edge, OUTLINE_POINTS)
        outline_x = np.concatenate(
            [xs, np.full_like(ys, right_edge), xs[::-1], np.full_like(ys, -0.5)]
        )
        outline_y = np.concatenate(
            [np.full_like(xs, -0.5), ys, np.full_like(xs, bottom_edge), ys[::-1]]
        )
        ra, dec = model.pixel_to_sky(outline_x, outline_y)

        outline = np.array(self._prepare_coords_many(list(zip(ra, dec))))
        data_x, data_y = outline[:, 0], outline[:, 1]
        ax, ay = self.canvas._to_axes(data_x, data_y)
        visible = np.isfinite(ax) & np.isfinite(ay)
        if not visible.any():
            self.canvas.logger.warning("Image is outside the plot, skipping")
            return

        dx, dy = self.canvas._to_display(data_x[visible], data_y[visible])
        left = max(0, int(np.floor(dx.min())))
        top = max(0, int(np.floor(dy.min())))
        right = min(int(np.ceil(self.canvas.width)), int(np.ceil(dx.max())))
        bottom = min(int(np.ceil(self.canvas.height)), int(np.ceil(dy.max())))

        if right <= left or bottom <= top:
            self.canvas.logger.warning("Image is outside the plot, skipping")
            return

        out = np.zeros((bottom - top, right - left, 4), dtype=np.uint8)
        cols = left + np.arange(right - left) + 0.5

        for start in range(0, bottom - top, CHUNK_ROWS):
            rows = top + np.arange(start, min(start + CHUNK_ROWS, bottom - top)) + 0.5
            grid_x, grid_y = np.meshgrid(cols, rows)
            ra, dec = self._data_to_radec(
                *self.canvas._from_display(grid_x.ravel(), grid_y.ravel())
            )

            finite = np.isfinite(ra) & np.isfinite(dec)
            px, py, valid = model.sky_to_pixel(
                np.where(finite, ra, 0), np.where(finite, dec, 0)
            )
            inside = (
                finite
                & valid
                & (px >= -0.5)
                & (px <= src_width - 0.5)
                & (py >= -0.5)
                & (py <= src_height - 0.5)
            )

            rgba = _sample_bilinear(
                source, np.where(inside, px, 0), np.where(inside, py, 0)
            )
            rgba[~inside, 3] = 0
            out[start : start + len(rows)] = np.rint(rgba).reshape(len(rows), -1, 4)

        buffer = io.BytesIO()
        Image.fromarray(out, "RGBA").save(buffer, format="PNG")
        href = "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode()

        with self.canvas.group(gid=gid):
            self.canvas.image(
                href,
                x=left,
                y=top,
                width=right - left,
                height=bottom - top,
                zorder=style.zorder,
                opacity=style.opacity,
            )
