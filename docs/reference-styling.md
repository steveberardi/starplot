# Styling Framework

Starplot has a styling framework that lets you fully customize the appearance of your plots. The framework consists of a bunch of [Pydantic models](https://docs.pydantic.dev/latest/usage/models/) that represent different things you can style (e.g. markers, lines, labels, etc). Since they're based on Pydantic models, this means you can define new styles through Python code, a JSON, or even a YAML file.

- [Basic Usage](#basic-usage)
- [Creating a Style](#creating-a-style)
- [Extending a Style](#extending-a-style)
- [Built-in Style Extensions](#built-in-style-extensions)
- [Code Reference](#code-reference)


## Basic Usage

When you create a plot, you can optionally pass in an instance of a [`PlotStyle`][starplot.PlotStyle]. This instance represents ALL the styling properties to use for the plot.

Using styles is usually a 3-step process:

1. Create a `PlotStyle` instance

2. Extend or override properties

3. Apply the style to the plot

Example:
```python
from starplot import MapPlot
from starplot.styles import PlotStyle, extensions

# Step 1: create a style
style = PlotStyle()

# Step 2: extend the style with a few built-in extensions
style = style.extend([
    extensions.MAP,
    extensions.BLUE_DARK
])

# Step 3: apply the style in a new map plot
mp = MapPlot(
    ra_min=3.6,
    ra_max=7.8,
    dec_min=-16,
    dec_max=23.6,
    style=style,
)

```

The sections below go into more detail around these steps.

## Creating a Style

Creating a style is simple:

```python
from starplot.styles import PlotStyle

style = PlotStyle()
```

After creating the style, you can modify properties of the style directly:

```python
style.star.marker.color = "red"
style.star.label.visible = False
```

This works well when you only want to change a couple properties, but for more complex styling it's easier to use PlotStyle's `extend` method which is explained in the next section.

## Extending a Style

Once you have an instance of a PlotStyle, then you can customize it with the PlotStyle's [`extend`](#starplot.PlotStyle.extend) method. This method takes a list of dictionaries and applies them to the original style in sequential order. In other words, when extending a PlotStyle, **you only have to define style properties that you want to override from the current style** — similar to how Cascading Style Sheets (CSS) work.

Starplot has a few [built-in extensions](#built-in-style-extensions) for applying color schemes, hiding labels, etc. But, you can also easily create your own extensions.


### Basic Example
Here's a simple example of extending a style to use a different font for Bayer labels of stars:

```python
from starplot import PlotStyle

style = PlotStyle().extend([{
    "bayer_labels": {
        "font_name": "GFS Didot",
        "font_size": 10
    }
}])
```
Alternatively, you can do this:
```python
style = PlotStyle()
style.bayer_labels.font_name = "GFS Didot"
style.bayer_labels.font_size = 10

```

### More Complex Example
The method above works well for overriding a few style properties, but if you want to create a more complex style then it's probably easier to define it in a YAML file and use PlotStyle's [`load_from_file`](#starplot.PlotStyle.load_from_file) static method.

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
from starplot import PlotStyle, MapPlot

style = PlotStyle.load_from_file("style.yml")

p = MapPlot(
    ra_min=3.6,
    ra_max=7.8,
    dec_min=-16,
    dec_max=23.6,
    style=style,
)

```

---
## Built-in Style Extensions

Starplot has a bunch of built-in style extensions (all imported from `starplot.styles.extensions`):

- **Color Schemes**
    - `GRAYSCALE` - Optimized for printing in grayscale ([details](#extensions-grayscale))
    - `BLUE_LIGHT` - Light and bright colors
    - `BLUE_MEDIUM` - Medium brightness bluish gray colors
    - `BLUE_DARK` - Dark bluish gray colors
- **Plot types**
    - `MAP_BASE`
    - `ZENITH_BASE`
- **Others**
    - `HIDE_LABELS` - Hides all the labels ([details](#extensions-hide-labels))


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

## Style Extensions

<h2 class="doc doc-heading" id="extensions-grayscale">
    <code>GRAYSCALE</code>
</h2>

<div class="indent" markdown>
Optimized for printing in grayscale

**Source**
```yaml
{% include 'hide_labels.yml' %}
```
</div>


<h2 class="doc doc-heading" id="extensions-hide-labels">
    <code>HIDE_LABELS</code>
</h2>

<div class="indent" markdown>
Hides all the labels

**Source**
```yaml
{% include 'hide_labels.yml' %}
```

</div>
