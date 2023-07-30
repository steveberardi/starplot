# Styling Framework

Starplot has a styling framework that lets you fully customize the appearance of your plots. The framework consists of a bunch of [Pydantic models](https://docs.pydantic.dev/latest/usage/models/) that represent different things you can style (e.g. markers, lines, labels, etc). Since they're based on Pydantic models, this means you can easily define new styles through a JSON (or even a YAML file).

- [Built-in Plot Styles](#built-in-plot-styles)
- [Extending an Existing PlotStyle](#extending-an-existing-plotstyle)
- [Creating a New PlotStyle](#creating-a-new-plotstyle)
- [Code Reference](#code-reference)


## Built-in Plot Styles

Starplot has five built-in styles:

TODO


## Extending an Existing PlotStyle

If there's an existing [PlotStyle][starplot.PlotStyle] that you just want to make some minor changes to, the easiest way to do that is through the PlotStyle's `extend` method. Here's an example of using it to create a new style that uses a different font for stars' Bayer labels:

```python
from starplot.styles import MAP_BLUE

style = MAP_BLUE.extend({
    "bayer_labels": {
        "font_name": "GFS Didot",
        "font_size": 10
    }
})
```
Alternatively, you can do this:
```python
style = MAP_BLUE
style.bayer_labels.font_name = "GFS Didot"
style.bayer_labels.font_size = 10

```

## Creating a New PlotStyle

To create a whole new style, you can do it through code, JSON, or YAML:

=== "Python"

    ```python
    ps = PlotStyle(
        background_color = "#fff",
        text_border_width = 2,
        text_offset_x = 0.005,
        text_offset_y = 0.005,

        # Borders
        border_font_size = 18,
        border_font_weight = FontWeightEnum.BOLD,
        border_font_color = "#000",
        border_line_color = "#000",
        border_bg_color = "#fff",

        # Stars
        star = ObjectStyle(
            marker=MarkerStyle(fillstyle=FillStyleEnum.FULL),
            label=LabelStyle(font_size=9, font_weight=FontWeightEnum.BOLD, zorder=1024),
        ),
        bayer_labels = LabelStyle(
            font_size=8, font_weight=FontWeightEnum.LIGHT, zorder=1024
        ),

        # Deep Sky Objects (DSOs)
        dso = ObjectStyle(
            marker=MarkerStyle(
                symbol=MarkerSymbolEnum.TRIANGLE, size=4, fillstyle=FillStyleEnum.FULL
            ),
            label=LabelStyle(font_size=8),
        ),

        # Constellations
        constellation = PathStyle(
            line=LineStyle(color="#c8c8c8"),
            label=LabelStyle(font_size=7, font_weight=FontWeightEnum.LIGHT),
        ),
        constellation_borders = LineStyle(
            color="#000", width=2, style=LineStyleEnum.DASHED, alpha=0.2, zorder=-100
        ),

        # Milky Way
        milky_way = PolygonStyle(
            color="#d9d9d9",
            alpha=0.36,
            edge_width=0,
            zorder=-10000,
        ),
    )
    ```

=== "JSON"

    ```json
    TODO
    ```

=== "YAML"

    ```yaml
    background_color: '#fff'
    bayer_labels:
        font_alpha: 1.0
        font_color: '#000'
        font_name: null
        font_size: 8
        font_style: normal
        font_weight: light
        visible: true
        zorder: 1024
    border_bg_color: '#fff'
    border_font_color: '#000'
    border_font_size: 18
    border_font_weight: bold
    border_line_color: '#000'
    constellation:
        label:
            font_alpha: 1.0
            font_color: '#000'
            font_name: null
            font_size: 7
            font_style: normal
            font_weight: light
            visible: true
            zorder: 1
        line:
            alpha: 1.0
            color: '#c8c8c8'
            style: solid
            width: 2
            zorder: -1
    constellation_borders:
        alpha: 0.2
        color: '#000'
        style: dashed
        width: 2
        zorder: -100
    dso:
        label:
            font_alpha: 1.0
            font_color: '#000'
            font_name: null
            font_size: 8
            font_style: normal
            font_weight: normal
            visible: true
            zorder: 1
        marker:
            alpha: 1.0
            color: '#000'
            fill: none
            size: 4
            symbol: ^
            visible: true
            zorder: -1
    milky_way:
        alpha: 0.36
        color: '#d9d9d9'
        edge_width: 0
        zorder: -10000
    star:
        label:
            font_alpha: 1.0
            font_color: '#000'
            font_name: null
            font_size: 9
            font_style: normal
            font_weight: bold
            visible: true
            zorder: 1024
        marker:
            alpha: 1.0
            color: '#000'
            fill: none
            size: 4
            symbol: .
            visible: true
            zorder: -1
    text_border_width: 2
    text_offset_x: 0.005
    text_offset_y: 0.005

    ```

!!! tip "Creating New Styles"

    As you can see in the examples above, creating a whole new style is easiest to do via a YAML file. Doing it in code is certainly possible, but the result is very verbose.

---

## Code Reference


::: starplot.PlotStyle
    options:
        show_root_heading: true
        show_docstring_attributes: true
        members: true


---
::: starplot.styles.MarkerStyle
    options:
        show_root_heading: true
        show_docstring_attributes: true


::: starplot.styles.LineStyle
    options:
        show_root_heading: true
        show_docstring_attributes: true

::: starplot.styles.PolygonStyle
    options:
        show_root_heading: true
        show_docstring_attributes: true

::: starplot.styles.LabelStyle
    options:
        show_root_heading: true
        show_docstring_attributes: true

---


::: starplot.styles.ObjectStyle
    options:
        show_root_heading: true
        show_docstring_attributes: true

::: starplot.styles.PathStyle
    options:
        show_root_heading: true
        show_docstring_attributes: true


---
::: starplot.styles.FillStyleEnum
    options:
        show_root_heading: true
        show_docstring_attributes: true
        members: true