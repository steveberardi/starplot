from pathlib import Path
from datetime import datetime

import pytest

from pytz import timezone

from starplot import styles, optics, OpticPlot, callables

from .utils import colorhash, dhash

HERE = Path(__file__).resolve().parent
DATA_PATH = HERE / "data"


@pytest.fixture()
def optic_style():
    yield styles.PlotStyle().extend(
        styles.extensions.GRAYSCALE_DARK,
        styles.extensions.OPTIC,
    )


@pytest.fixture()
def dt_dec_16():
    yield datetime.now(timezone("US/Pacific")).replace(2023, 12, 16, 21, 0, 0)


def test_optic_plot_binoculars_m45(optic_style, dt_dec_16):
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
        style=optic_style,
        resolution=1600,
    )
    optic_plot.stars(mag=12)
    optic_plot.info()
    filename = DATA_PATH / "optic-binoculars-m45.png"
    optic_plot.export(filename)

    assert dhash(filename) == "8e172b5133338e4d"
    assert colorhash(filename) == "33000000000"


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
        style=optic_style,
        resolution=1600,
    )
    optic_plot.stars(mag=14)
    optic_plot.info()
    filename = DATA_PATH / "optic-binoculars-polaris.png"
    optic_plot.export(filename)

    assert dhash(filename) == "167140cc4c611355"
    assert colorhash(filename) == "07000000000"


def test_optic_plot_refractor_double(optic_style, dt_dec_16):
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
        style=optic_style,
        resolution=1600,
    )
    optic_plot.stars(mag=12)
    optic_plot.info()
    filename = DATA_PATH / "optic-refractor-double-cluster.png"
    optic_plot.export(filename)

    assert dhash(filename) == "8e172b552b338e4d"
    assert colorhash(filename) == "33000000000"


def test_optic_plot_wrapping(optic_style, dt_dec_16):
    style = optic_style.extend(
        {
            "star": {
                "marker": {
                    "symbol": "star",
                    "size": 90,
                }
            }
        }
    )
    optic_plot = OpticPlot(
        ra=23.99,
        dec=17.2738888889,
        lat=32.97,
        lon=-117.038611,
        # use binoculars for a wide TFOV
        optic=optics.Binoculars(
            magnification=8,
            fov=65,
        ),
        dt=dt_dec_16,
        style=style,
        resolution=1600,
    )
    optic_plot.stars(mag=12)
    optic_plot.info()
    filename = DATA_PATH / "optic-wrapping.png"
    optic_plot.export(filename)

    assert dhash(filename) == "8e172b452b338e4d"
    assert colorhash(filename) == "1e000000000"


def test_optic_plot_scope_m45(optic_style, dt_dec_16):
    optic_plot = OpticPlot(
        # M45
        ra=3.7836111111,
        dec=24.1166666667,
        lat=32.97,
        lon=-117.038611,
        optic=optics.Scope(
            focal_length=600,
            eyepiece_focal_length=14,
            eyepiece_fov=82,
        ),
        dt=dt_dec_16,
        style=optic_style,
        resolution=1600,
    )
    optic_plot.stars(mag=12, color_fn=callables.color_by_bv)
    optic_plot.info()
    filename = DATA_PATH / "optic-scope-m45.png"
    optic_plot.export(filename)

    assert dhash(filename) == "8e172b5133338e4d"
    assert colorhash(filename) == "33e00000000"


def test_optic_plot_reflector_m45(optic_style, dt_dec_16):
    optic_plot = OpticPlot(
        # M45
        ra=3.7836111111,
        dec=24.1166666667,
        lat=32.97,
        lon=-117.038611,
        optic=optics.Reflector(
            focal_length=600,
            eyepiece_focal_length=14,
            eyepiece_fov=82,
        ),
        dt=dt_dec_16,
        style=optic_style,
        resolution=1600,
    )
    optic_plot.stars(mag=12)
    optic_plot.info()
    filename = DATA_PATH / "optic-reflector-m45.png"
    optic_plot.export(filename)

    assert dhash(filename) == "8e173b512b338e4d"
    assert colorhash(filename) == "33000000000"


def test_optic_plot_camera_m45(optic_style, dt_dec_16):
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
        style=optic_style,
        resolution=1600,
    )
    optic_plot.stars(mag=12)
    optic_plot.info()
    filename = DATA_PATH / "optic-camera-m45.png"
    optic_plot.export(filename)

    assert dhash(filename) == "4d71715171654d75"
    # flaky - seems the colorhash can vary for this plot?
    assert colorhash(filename) == "3a000000000"


def test_optic_plot_camera_rotated(optic_style, dt_dec_16):
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
            rotation=40,
        ),
        dt=dt_dec_16,
        style=optic_style,
        resolution=1600,
    )
    optic_plot.stars(mag=12)
    optic_plot.info()
    filename = DATA_PATH / "optic-camera-rotated-m45.png"
    optic_plot.export(filename)

    assert dhash(filename) == "25468b33269d9a65"
    assert colorhash(filename) == "17000000000"


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
