import pytest

from pydantic import ValidationError
from pydantic.color import Color

from starplot.styles import PlotStyle, FontWeightEnum, LineStyle, LineStyleEnum


@pytest.mark.parametrize(
    "kwargs",
    [
        dict(
            background_color="#fff",
        ),
        dict(background_color=Color("#ff8e8e")),
        dict(background_color="rgb(12,12,12)"),
        dict(star_font_weight=FontWeightEnum.BOLD),
        dict(background_color="#fff", constellation_line_width=2),
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
    ],
)
def test_plot_style_invalid(kwargs):
    with pytest.raises(ValidationError):
        PlotStyle(**kwargs)


def test_style_enums_use_strings():
    line_style = LineStyle(style=LineStyleEnum.DASHED)
    assert line_style.style == "dashed"
