import pytest

from starplot import Binoculars, Camera, OpticPlot, Observer, styles


def test_optic_plot_raises_fov_too_big():
    with pytest.raises(ValueError, match=r"Field of View too big"):
        OpticPlot(
            ra=2.51667,
            dec=89.26,
            observer=Observer(
                lat=32.97,
                lon=-117.038611,
            ),
            optic=Binoculars(
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
            observer=Observer(
                lat=32.97,
                lon=-117.038611,
            ),
            optic=Binoculars(
                magnification=10,
                fov=65,
            ),
        )


def test_optic_plot_raises_gradient_on_camera():
    with pytest.raises(
        ValueError, match=r"Gradient backgrounds are not yet supported for cameras"
    ):
        OpticPlot(
            ra=2.51667,
            dec=89.26,
            observer=Observer(
                lat=32.97,
                lon=-117.038611,
            ),
            optic=Camera(
                lens_focal_length=400,
                sensor_height=24,
                sensor_width=35,
            ),
            style=styles.PlotStyle().extend(styles.extensions.GRADIENT_PRE_DAWN),
        )


def test_optic_plot_allows_gradient_on_non_camera():
    assert OpticPlot(
        ra=2.51667,
        dec=89.26,
        observer=Observer(
            lat=32.97,
            lon=-117.038611,
        ),
        optic=Binoculars(
            magnification=10,
            fov=65,
        ),
        style=styles.PlotStyle().extend(styles.extensions.GRADIENT_PRE_DAWN),
    )
