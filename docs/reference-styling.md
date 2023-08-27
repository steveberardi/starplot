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

The easiest way to create a whole new style is by defining it in a YAML file. **You only have to define style properties that you want to override from the default base style** — similar to how Cascading Style Sheets (CSS) work.

Example:


```yaml
# style.yml

# hide the constellation labels/lines:
constellation:
  label:
    visible: false
  line:
    visible: false

# make the Milky Way gray
milky_way:
  alpha: 0.36
  color: '#888'

# change the color of star labels to blue and
# and change their symbol from dots to stars
star:
  label:
    font_color: '#0e69b8'
  marker:
    symbol: *

# make nebulas green and their markers diamonds
dso_nebula:
  marker:
    color: green
    symbol: D

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

