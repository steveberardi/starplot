from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from starplot import Binoculars, NakedEye, Observer, OpticPlot, styles
from starplot.plots.optic import GRID_STEPS, _multiples, _nice_step, degrees_label


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


def _orion_plot(optic):
    return OpticPlot(
        ra=84.0534,
        dec=-1.2019,
        observer=Observer(
            dt=datetime(2025, 12, 21, 19, 0, tzinfo=ZoneInfo("America/Los_Angeles")),
            lat=32.9628,
            lon=-117.0359,
        ),
        optic=optic,
    )


def test_optic_plot_plots_gridlines():
    # GIVEN an optic plot
    p = _orion_plot(NakedEye())

    # WHEN plotting gridlines
    p.gridlines()

    # THEN the gridlines are in the rendered plot
    svg = p.canvas.render()
    assert 'id="gridlines"' in svg
    assert "<polyline" in svg


def test_optic_plot_gridlines_accept_custom_locations():
    p = _orion_plot(NakedEye())
    p.gridlines(az_locations=[100, 105], alt_locations=[20], labels=False)

    svg = p.canvas.render()
    start = svg.find('id="gridlines"')
    assert svg[start : svg.find("</g>", start)].count("<polyline") == 3


def test_optic_plot_gridlines_are_labeled_outside_the_plot():
    p = _orion_plot(NakedEye())
    p.gridlines(az_locations=[105], alt_locations=[20])

    svg = p.canvas.render()
    assert "105\N{DEGREE SIGN}" in svg
    assert "20\N{DEGREE SIGN}" in svg


def test_optic_plot_gridline_labels_can_be_hidden():
    p = _orion_plot(NakedEye())
    p.gridlines(az_locations=[105], alt_locations=[20], labels=False)

    assert "105\N{DEGREE SIGN}" not in p.canvas.render()


def test_optic_plot_gridlines_use_custom_label_functions():
    p = _orion_plot(NakedEye())
    p.gridlines(
        az_locations=[105],
        alt_locations=[],
        az_label_fn=lambda az: "CUSTOM AZ",
    )

    assert "CUSTOM AZ" in p.canvas.render()


def test_optic_plot_gridlines_label_cardinal_directions():
    p = _orion_plot(NakedEye())
    p.gridlines(az_locations=[90], alt_locations=[])

    assert "EAST" in p.canvas.render()


def test_gridline_step_grows_with_the_field_of_view():
    # a narrow field of view gets fine spacing, and a wide one gets coarse spacing
    assert _nice_step(0.6, GRID_STEPS) == 1
    assert _nice_step(10, GRID_STEPS) == 10
    assert _nice_step(1000, GRID_STEPS) == GRID_STEPS[-1]


def test_gridline_multiples_stay_within_the_limits():
    assert _multiples(10, -25, 25) == [-20, -10, 0, 10, 20]
    assert _multiples(15, 100, 140) == [105, 120, 135]


def test_degrees_label_only_includes_parts_that_are_needed():
    assert degrees_label(10) == "10\N{DEGREE SIGN}"
    assert degrees_label(-5.5) == "-5\N{DEGREE SIGN} 30\N{PRIME}"
    assert degrees_label(0) == "0\N{DEGREE SIGN}"
    assert degrees_label(-0.25) == "-0\N{DEGREE SIGN} 15\N{PRIME}"
