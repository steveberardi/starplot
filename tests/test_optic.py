import pytest

from starplot import optics, OpticPlot


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
