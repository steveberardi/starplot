from pathlib import Path
from datetime import datetime

from pytz import timezone

import pytest

from starplot import styles, optic, OpticPlot

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
        optic=optic.Binoculars(
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

    assert dhash(filename) == "8e17695545330f4d"
    assert colorhash(filename) == "33e00000000"


def test_optic_plot_camera(optic_style, dt_dec_16):
    optic_plot = OpticPlot(
        # M45
        ra=3.7836111111,
        dec=24.1166666667,
        lat=32.97,
        lon=-117.038611,
        # Fuji X-T2
        optic=optic.Camera(
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

    assert dhash(filename) == "4d55515575454d55"
    assert colorhash(filename) in ["3ae00008000", "3ac00008000"]