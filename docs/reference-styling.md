# Styling Framework

Starplot has a styling framework that lets you fully customize the appearance of your plots. The framework consists of a bunch of [Pydantic models](https://docs.pydantic.dev/latest/usage/models/) that represent different things you can style (e.g. markers, lines, labels, etc). Since they're based on Pydantic models, this means you can easily define new styles through a JSON (or even a YAML file).

- [Built-in Plot Styles](#built-in-plot-styles)
- [Extending an Existing PlotStyle](#extending-an-existing-plotstyle)
- [Creating a New PlotStyle](#creating-a-new-plotstyle)
- [Code Reference](#code-reference)


## Built-in Plot Styles

Starplot has five built-in styles (all imported from `starplot.styles`):


- `GRAYSCALE` - Optimized for printing in grayscale (the default for `ZenithPlot`)

- `BLUE` - Grayish blue colors

- `CHALK` - Low saturation/contrast

- `RED` - Everything red

- `MAP_BLUE` - Similar to the `BLUE` style, but more tailored for maps (the default for `MapPlot`)


## Extending an Existing PlotStyle

If there's an existing [PlotStyle][starplot.PlotStyle] that you just want to make some minor changes to, then you can use the PlotStyle's `extend` method.

Here's an example of extending the `MAP_BLUE` style to use a different font for Bayer labels of stars:

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

The easiest way to create a whole new style is by defining it in a YAML file, for example:


```yaml
# style.yml

background_color: '#fff'
bayer_labels:
  font_alpha: 1.0
  font_color: '#000'
  font_name: null
  font_size: 7
  font_style: normal
  font_weight: light
  visible: true
  zorder: 1024
border_bg_color: '#7997b9'
border_font_color: '#f1f6ff'
border_font_size: 18
border_font_weight: bold
border_line_color: '#2f4358'
constellation:
  label:
    font_alpha: 1.0
    font_color: '#c5c5c5'
    font_name: null
    font_size: 11
    font_style: normal
    font_weight: light
    visible: true
    zorder: 1
  line:
    alpha: 0.34
    color: '#6ba832'
    style: solid
    visible: true
    width: 3
    zorder: -1
constellation_borders:
  alpha: 0.2
  color: '#000'
  style: dashed
  visible: true
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
  alpha: 0.16
  color: '#94c5e3'
  edge_width: 0
  visible: true
  zorder: -10000
star:
  label:
    font_alpha: 1.0
    font_color: '#000'
    font_name: null
    font_size: 8
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

Then, to use your new style:

```python
import starplot as sp

# load the style
style = sp.styles.PlotStyle.load_from_file("style.yml")

p = sp.MapPlot(
    ra_min=3.6,
    ra_max=7.8,
    dec_min=-16,
    dec_max=23.6,
    style=style,
)

```


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

::: starplot.styles.FontStyleEnum
    options:
        show_root_heading: true
        show_docstring_attributes: true
        members: true

::: starplot.styles.FontWeightEnum
    options:
        show_root_heading: true
        show_docstring_attributes: true
        members: true

::: starplot.styles.LineStyleEnum
    options:
        show_root_heading: true
        show_docstring_attributes: true
        members: true

::: starplot.styles.MarkerSymbolEnum
    options:
        show_root_heading: true
        show_docstring_attributes: true
        members: true

