import pytest
from pydantic import ValidationError
from pydantic_extra_types.color import Color

from starplot import MapPlot, Miller
from starplot.styles import (
    DashArray,
    FontWeight,
    LineStyle,
    PlotStyle,
    extensions,
    use_style,
)


@pytest.mark.parametrize(
    "kwargs",
    [
        dict(axes={"background": {"fill": "#fff"}}),
        dict(axes={"background": {"fill": Color("#ff8e8e")}}),
        dict(axes={"background": {"fill": "rgb(1,2,3)"}}),
        dict(star={"label": {"font_weight": FontWeight.BOLD}}),
        dict(
            axes={"background": {"fill": "#fff"}},
            constellation={"line": {"width": 2}},
        ),
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
        dict(axes={"background": {"fill": 2}}),
        dict(axes={"background": {"fill": "rgb(1,1,1,1,1,1,1,1,1)"}}),
        dict(constellation="hello"),
        dict(star={"label": {"font_weight": "invalid"}}),
        dict(extra_stuff="hello"),
    ],
)
def test_plot_style_invalid(kwargs):
    with pytest.raises(ValidationError):
        PlotStyle(**kwargs)


def test_style_enums_use_strings():
    line_style = LineStyle(dash_array=DashArray.DASHED)
    assert line_style.dash_array == "dashed"


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


def test_extend_nested_star_and_constellation_styles():
    style = PlotStyle().extend(
        {
            "star": {"bayer_label": {"font_size": 99}},
            "constellation": {"line": {"width": 7}, "border": {"width": 3}},
        }
    )

    assert style.star.bayer_label.font_size == 99
    assert style.star.flamsteed_label.font_size == 26
    assert style.star.marker.size == 20
    assert style.constellation.line.width == 7
    assert style.constellation.border.width == 3
    assert style.constellation.label.font_size == 40


@pytest.mark.parametrize(
    "extension",
    [
        value
        for name, value in vars(extensions).items()
        if name.isupper() and isinstance(value, dict)
    ],
)
def test_extensions_are_valid_for_plot_style(extension):
    PlotStyle().extend(extension)


def test_use_style_resolves_nested_style_attr():
    class Plot:
        style = PlotStyle().extend({"constellation": {"line": {"width": 7}}})

        @use_style(LineStyle, "constellation.line")
        def draw(self, style: LineStyle = None):
            return style

    plot = Plot()

    # uses the plot's style by default
    assert plot.draw().width == 7

    # merges kwarg overrides into the plot's style
    overridden = plot.draw(style__stroke="#f00")
    assert overridden.width == 7
    assert overridden.stroke.as_hex() == "#f00"

    # merges dict overrides into the plot's style
    assert plot.draw(style={"width": 2}).stroke.as_hex() == "#c8c8c8"
