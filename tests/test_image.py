import base64
import io
import re
from datetime import UTC, datetime

import numpy as np
import pytest
from PIL import Image, ImageDraw

from starplot import (
    Binoculars,
    HorizonPlot,
    MapPlot,
    Mercator,
    Observer,
    OpticPlot,
    PlotStyle,
    Stereographic,
)
from starplot.plotters.image import PixelSkyModel, _inverse_gnomonic
from starplot.styles import ImageStyle, ZOrder

# 400x300 px image centered on (RA 100, Dec 20), at 0.05 degrees per pixel, with RA increasing to the left
SCALE = np.radians(0.05)


def sky(x, y, center=(100, 20)):
    ra, dec = _inverse_gnomonic(-(x - 200) * SCALE, -(y - 150) * SCALE, *center)
    return float(ra), float(dec)


CONTROL_POINTS = [
    ((x, y), sky(x, y)) for x, y in [(0, 0), (400, 0), (0, 300), (400, 300)]
]


@pytest.fixture
def photo():
    img = Image.new("RGB", (400, 300), (30, 60, 120))
    ImageDraw.Draw(img).ellipse((90, 190, 110, 210), fill=(255, 0, 0))
    return img


@pytest.fixture
def plot():
    return MapPlot(
        projection=Stereographic(center_ra=100, center_dec=20),
        ra_min=85,
        ra_max=115,
        dec_min=8,
        dec_max=32,
        resolution=800,
    )


def embedded_image(svg: str) -> tuple[Image.Image, float, float]:
    """Returns the embedded PNG and its (x, y) position in the plot"""
    tag = re.search(r"<image [^>]*/>", svg).group(0)
    x = float(re.search(r' x="([^"]+)"', tag).group(1))
    y = float(re.search(r' y="([^"]+)"', tag).group(1))
    data = re.search(r'href="data:image/png;base64,([^"]+)"', tag).group(1)
    return Image.open(io.BytesIO(base64.b64decode(data))).convert("RGBA"), x, y


def test_model_round_trip():
    model = PixelSkyModel(CONTROL_POINTS)

    ra, dec = model.pixel_to_sky(np.array([100.0, 0, 400]), np.array([200.0, 0, 300]))
    assert (ra[0], dec[0]) == pytest.approx(sky(100, 200), abs=0.01)

    px, py, valid = model.sky_to_pixel(ra, dec)
    assert valid.all()
    assert px == pytest.approx([100, 0, 400], abs=1e-3)
    assert py == pytest.approx([200, 0, 300], abs=1e-3)


def test_model_ra_wraparound():
    points = [
        ((0, 0), (359.0, 10.0)),
        ((100, 0), (357.0, 10.0)),
        ((0, 100), (359.0, 8.0)),
    ]
    model = PixelSkyModel(points)
    ra, dec = model.pixel_to_sky(np.array([50.0]), np.array([50.0]))
    assert ra[0] == pytest.approx(358.0, abs=1e-2)
    assert dec[0] == pytest.approx(9.0, abs=1e-2)


def test_model_requires_three_points():
    with pytest.raises(ValueError, match="At least 3"):
        PixelSkyModel(CONTROL_POINTS[:2])


def test_model_rejects_collinear_points():
    points = [((x, 150), sky(x, 150)) for x in (0, 200, 400)]
    with pytest.raises(ValueError, match="single line"):
        PixelSkyModel(points)


def test_image_lands_on_sky_position(plot, photo):
    plot.image(photo, CONTROL_POINTS)
    out, left, top = embedded_image(plot.canvas.render())

    red = np.argwhere(
        (np.asarray(out)[..., 0] > 200)
        & (np.asarray(out)[..., 1] < 50)
        & (np.asarray(out)[..., 3] == 255)
    )
    row, col = red.mean(axis=0)

    expected_x, expected_y = plot.canvas._to_display(*sky(100, 200))
    assert left + col + 0.5 == pytest.approx(expected_x, abs=2)
    assert top + row + 0.5 == pytest.approx(expected_y, abs=2)


def test_image_is_transparent_outside_footprint(plot, photo):
    plot.image(photo, CONTROL_POINTS)
    out, _, _ = embedded_image(plot.canvas.render())
    alpha = np.asarray(out)[..., 3]

    # the projection skews the image, so its bounding box has empty slivers
    assert alpha.min() == 0
    assert (alpha == 255).sum() > 0.8 * alpha.size


def test_image_gid(plot, photo):
    plot.image(photo, CONTROL_POINTS, gid="my-photo")

    assert 'id="my-photo"' in plot.canvas.render()


def test_image_style_object(plot, photo):
    plot.image(photo, CONTROL_POINTS, style=ImageStyle(opacity=0.4))

    assert 'opacity="0.4"' in plot.canvas.render()


def test_image_style_dict_and_kwargs(plot, photo):
    plot.image(photo, CONTROL_POINTS, style={"opacity": 0.3})
    assert 'opacity="0.3"' in plot.canvas.render()

    plot.image(photo, CONTROL_POINTS, style__opacity=0.2)
    assert 'opacity="0.2"' in plot.canvas.render()


def test_image_uses_plot_style(photo):
    style = PlotStyle()
    style.image.opacity = 0.5
    plot = MapPlot(
        projection=Stereographic(center_ra=100, center_dec=20),
        ra_min=85,
        ra_max=115,
        dec_min=8,
        dec_max=32,
        resolution=800,
        style=style,
    )
    plot.image(photo, CONTROL_POINTS)

    assert 'opacity="0.5"' in plot.canvas.render()


def test_image_style_rejects_invalid_opacity():
    with pytest.raises(ValueError):
        ImageStyle(opacity=1.5)


def test_image_zorder_from_style(plot, photo):
    plot.marker(100, 20)
    plot.image(photo, CONTROL_POINTS, style=ImageStyle(zorder=ZOrder.LAYER_5))

    svg = plot.canvas.render()
    assert svg.index("<circle") < svg.index("<image ")


def test_image_from_file(plot, photo, tmp_path):
    path = tmp_path / "photo.png"
    photo.save(path)

    plot.image(path, CONTROL_POINTS)

    assert "<image " in plot.canvas.render()


def test_image_outside_plot_is_skipped(photo):
    plot = MapPlot(
        projection=Mercator(),
        ra_min=200,
        ra_max=230,
        dec_min=-20,
        dec_max=10,
        resolution=400,
    )
    plot.image(photo, CONTROL_POINTS)

    assert "<image " not in plot.canvas.render()


def test_image_below_stars_by_default(plot, photo):
    plot.image(photo, CONTROL_POINTS)
    plot.marker(100, 20)

    svg = plot.canvas.render()
    assert svg.index("<image ") < svg.index("<circle")


def alt_az_plots():
    """Returns (plot, image center RA/DEC) for each plot type that uses alt/az coordinates"""
    observer = Observer(dt=datetime(2024, 6, 1, 4, tzinfo=UTC), lat=33.0, lon=-117.0)

    # Low altitude, so atmospheric refraction is part of what's being checked
    horizon = HorizonPlot(
        altitude=(2, 32), azimuth=(105, 135), observer=observer, resolution=800
    )
    horizon_center = observer.radec(120, 17)

    optic_center = observer.radec(180, 40)
    optic = OpticPlot(
        ra=optic_center[0],
        dec=optic_center[1],
        observer=observer,
        optic=Binoculars(magnification=1.5, fov=30),
        resolution=800,
    )
    return [(horizon, horizon_center), (optic, optic_center)]


@pytest.mark.parametrize("index", [0, 1], ids=["horizon", "optic"])
def test_image_on_alt_az_plot_lands_on_sky_position(photo, index):
    plot, center = alt_az_plots()[index]
    points = [
        ((x, y), sky(x, y, center)) for x, y in [(0, 0), (400, 0), (0, 300), (400, 300)]
    ]

    plot.image(photo, points)
    out, left, top = embedded_image(plot.canvas.render())

    mask = (
        (np.asarray(out)[..., 0] > 200)
        & (np.asarray(out)[..., 1] < 50)
        & (np.asarray(out)[..., 3] == 255)
    )
    row, col = np.argwhere(mask).mean(axis=0)

    expected_x, expected_y = plot.canvas._to_display(
        *plot._prepare_coords(*sky(100, 200, center))
    )
    assert left + col + 0.5 == pytest.approx(expected_x, abs=2)
    assert top + row + 0.5 == pytest.approx(expected_y, abs=2)
