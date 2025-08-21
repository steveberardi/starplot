import pytest

from pydantic import ValidationError
from pydantic.color import Color

from starplot import MapPlot, Miller
from starplot.styles import PlotStyle, FontWeightEnum, LineStyle, LineStyleEnum


@pytest.mark.parametrize(
    "kwargs",
    [
        dict(
            background_color="#fff",
        ),
        dict(background_color=Color("#ff8e8e")),
        dict(background_color="rgb(12,12,12)"),
        dict(star={"label": {"font_weight": FontWeightEnum.BOLD}}),
        dict(background_color="#fff", constellation_lines={"width": 2}),
    ],
)
def test_plot_style_valid(kwargs):
    try:
        PlotStyle(**kwargs)
    except ValidationError:
        pytest.fail("Unexpected ValidationError")


@pytest.mark.parametrize(
    "kwargs",
    [
        dict(background_color=2),
        dict(background_color=None),
        dict(background_color="rgb(12,12,12,12,12)"),
        dict(background_color="#fff", constellation="hello"),
        dict(star={"label": {"font_weight": "invalid"}}),
        dict(background_color="#fff", extra_stuff="hello"),
    ],
)
def test_plot_style_invalid(kwargs):
    with pytest.raises(ValidationError):
        PlotStyle(**kwargs)


def test_style_enums_use_strings():
    line_style = LineStyle(style=LineStyleEnum.DASHED)
    assert line_style.style == "dashed"


def test_style_context_manager():
    # GIVEN a font size of 128 for open cluster labels
    style = {"dso_open_cluster": {"label": {"font_size": 128}}}
    p = MapPlot(projection=Miller(), style=PlotStyle().extend(style))

    assert p.style.dso_open_cluster.label.font_size == 128

    # WHEN I override the font size in a context manager
    with p.style.dso_open_cluster as oc:
        oc.label.font_size = 32
        # THEN the plot's style should return this override value
        assert p.style.dso_open_cluster.label.font_size == 32

    # AND when I exit the context manager, it should revert to the original style
    assert p.style.dso_open_cluster.label.font_size == 128
