from pathlib import Path
from datetime import datetime

import pytest

from pytz import timezone

from starplot import styles, optics, OpticPlot

from .utils import colorhash, dhash

HERE = Path(__file__).resolve().parent
DATA_PATH = HERE / "data"


@pytest.fixture()
def optic_style():
    yield styles.PlotStyle().extend(
        styles.extensions.MINIMAL,
        styles.extensions.GRAYSCALE_DARK,
        styles.extensions.OPTIC,
    )


@pytest.fixture()
def dt_dec_16():
    yield datetime.now(timezone("US/Pacific")).replace(2023, 12, 16, 21, 0, 0)


def test_optic_plot_binoculars(optic_style, dt_dec_16):
    optic_plot = OpticPlot(
        # M45
        ra=3.7836111111,
        dec=24.1166666667,
        lat=32.97,
        lon=-117.038611,
        # 10x binoculars
        optic=optics.Binoculars(
            magnification=10,
            fov=65,
        ),
        dt=dt_dec_16,
        limiting_magnitude=12,
        style=optic_style,
        resolution=1600,
        include_info_text=True,
        colorize_stars=True,
    )
    filename = DATA_PATH / "actual-optic-binoculars-m45.png"
    optic_plot.export(filename)

    assert dhash(filename) == "8e172b552b338e4d"
    assert colorhash(filename) == "33e00000000"


def test_optic_plot_refractor(optic_style, dt_dec_16):
    optic_plot = OpticPlot(
        # double cluster
        ra=2.33,
        dec=57.14,
        lat=32.97,
        lon=-117.038611,
        # TV-85 with ES 14mm 82deg
        optic=optics.Refractor(
            focal_length=600,
            eyepiece_focal_length=14,
            eyepiece_fov=82,
        ),
        dt=dt_dec_16,
        limiting_magnitude=12,
        style=optic_style,
        resolution=1600,
        include_info_text=True,
        colorize_stars=True,
    )
    filename = DATA_PATH / "actual-optic-refractor-double-cluster.png"
    optic_plot.export(filename)

    assert dhash(filename) == "8e172b452b338e4d"
    assert colorhash(filename) == "33e00000000"


def test_optic_plot_camera(optic_style, dt_dec_16):
    optic_plot = OpticPlot(
        # M45
        ra=3.7836111111,
        dec=24.1166666667,
        lat=32.97,
        lon=-117.038611,
        # Fuji X-T2
        optic=optics.Camera(
            sensor_height=15.6,
            sensor_width=23.6,
            lens_focal_length=430,
        ),
        dt=dt_dec_16,
        limiting_magnitude=12,
        style=optic_style,
        resolution=1600,
        include_info_text=True,
        colorize_stars=True,
    )
    filename = DATA_PATH / "actual-optic-camera-m45.png"
    optic_plot.export(filename)

    assert dhash(filename) == "4171515165614975"
    assert colorhash(filename) in ["3ae00008000", "3ac00008000"]


def test_optic_plot_polaris_binoculars(dt_dec_16):
    optic_style = styles.PlotStyle().extend(
        styles.extensions.GRAYSCALE,
        styles.extensions.OPTIC,
    )
    optic_plot = OpticPlot(
        # Polaris
        ra=2.51667,
        dec=89.26,
        lat=32.97,
        lon=-117.038611,
        # 10x binoculars
        optic=optics.Binoculars(
            magnification=10,
            fov=65,
        ),
        dt=dt_dec_16,
        limiting_magnitude=14,
        style=optic_style,
        resolution=1600,
        include_info_text=True,
        colorize_stars=False,
    )
    filename = DATA_PATH / "actual-optic-binoculars-polaris.png"
    optic_plot.export(filename)

    assert dhash(filename) == "063140cc48611355"
    assert colorhash(filename) == "07000000000"


def test_optic_plot_raises_fov_too_big():
    with pytest.raises(ValueError, match=r"Field of View too big"):
        OpticPlot(
            ra=2.51667,
            dec=89.26,
            lat=32.97,
            lon=-117.038611,
            optic=optics.Binoculars(
                magnification=2,
                fov=100,
            ),
        )


def test_optic_plot_raises_on_below_horizon():
    with pytest.raises(
        ValueError, match=r"Target is below horizon at specified time/location."
    ):
        OpticPlot(
            ra=2.51667,
            dec=-88,  # should always be below horizon from California
            lat=32.97,
            lon=-117.038611,
            optic=optics.Binoculars(
                magnification=10,
                fov=65,
            ),
        )
