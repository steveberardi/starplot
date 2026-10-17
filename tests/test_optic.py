from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from starplot import Binoculars, NakedEye, Observer, OpticPlot, styles


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
                fov=140,
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


def test_optic_plot_allows_gradient():
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


def test_optic_plot_plots_constellation_lines():
    # GIVEN an optic plot centered on Orion's belt
    p = OpticPlot(
        ra=84.0534,
        dec=-1.2019,
        observer=Observer(
            dt=datetime(2025, 12, 21, 19, 0, tzinfo=ZoneInfo("America/Los_Angeles")),
            lat=32.9628,
            lon=-117.0359,
        ),
        optic=NakedEye(),
    )

    # WHEN plotting constellations
    p.constellations()
    p.constellation_borders()
    p.constellation_labels()

    # THEN Orion is among the plotted constellations
    assert "ori" in [c.iau_id for c in p._objects.constellations]


def test_optic_plot_plots_horizon():
    # GIVEN an optic plot that includes the horizon
    p = OpticPlot(
        ra=84.0534,
        dec=-1.2019,
        observer=Observer(
            dt=datetime(2025, 12, 21, 19, 0, tzinfo=ZoneInfo("America/Los_Angeles")),
            lat=32.9628,
            lon=-117.0359,
        ),
        optic=NakedEye(),
        style=styles.PlotStyle().extend(styles.extensions.OPTIC),
    )

    # WHEN plotting the horizon
    p.horizon()

    # THEN the horizon is in the rendered plot
    svg = p.canvas.render()
    assert "<polyline" in svg
    assert 'stroke-dasharray="' in svg
    assert "HORIZON" in svg


def test_optic_plot_horizon_label_can_be_hidden():
    p = OpticPlot(
        ra=84.0534,
        dec=-1.2019,
        observer=Observer(
            dt=datetime(2025, 12, 21, 19, 0, tzinfo=ZoneInfo("America/Los_Angeles")),
            lat=32.9628,
            lon=-117.0359,
        ),
        optic=NakedEye(),
    )
    p.horizon(label=None)
    assert "HORIZON" not in p.canvas.render(text_as_path=False)
