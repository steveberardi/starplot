# Styling Framework

Starplot has a styling framework that lets you fully customize the appearance of your plots. The framework consists of a collection of [Pydantic models](https://docs.pydantic.dev/latest/usage/models/) that represent different things you can style (e.g. markers, lines, labels, etc). Since they're based on Pydantic models, this means you can define new styles through Python code, a JSON, or even a YAML file.

- [Basic Usage](#basic-usage)
- [Creating a Style](#creating-a-style)
- [Extending a Style](#extending-a-style)
- [Overriding a Style at plot time](#overriding-styles-when-plotting)
- [Built-in Style Extensions](extensions.md)
- [Code Reference](reference.md)


## Basic Usage

When you create a plot, you can optionally pass in an instance of a [`PlotStyle`][starplot.PlotStyle]. This instance represents ALL the styling properties to use for the plot.

Using styles is usually a 3-step process:

1. Create a `PlotStyle` instance

2. Extend or override properties

3. Apply the style to the plot

Example:
<div class="tutorial" markdown>
```python linenums="1"
from starplot import MapPlot, Miller
from starplot.styles import PlotStyle, extensions

# Step 1: create a style
style = PlotStyle()

# Step 2: extend the style with a few built-in extensions
style = style.extend(
    extensions.BLUE_LIGHT,
    extensions.MAP,
)

# Step 3: apply the style in a new map plot
mp = MapPlot(
    projection=Miller(),
    ra_min=4,
    ra_max=8,
    dec_min=0,
    dec_max=20,
    style=style,
)
```
</div>

The sections below go into more detail around these steps.

## Creating a Style

Creating a style is simple:

```python
from starplot.styles import PlotStyle

style = PlotStyle()
```

After creating the style, you can modify properties of the style directly:

```python
style.star.marker.fill = "red"
style.star.label.font_size = 20
```

This works well when you only want to change a couple properties, but for more complex styling it's easier to use PlotStyle's `extend` method which is explained in the next section.

## Extending a Style

Once you have an instance of a PlotStyle, then you can customize it with the PlotStyle's [`extend`](reference.md#starplot.PlotStyle.extend) method. This method takes in one or more args of dictionaries and applies them to the original style in sequential order. In other words, when extending a PlotStyle, **you only have to define style properties that you want to override from the current style** — similar to how Cascading Style Sheets (CSS) work.

Starplot has a few [built-in extensions](extensions.md) for applying color schemes and optimizing different plot types. But, you can also easily create your own extensions.

### Basic Example
Here's a simple example of extending a style to use a different font for Bayer labels of stars:

```python
from starplot import PlotStyle

style = PlotStyle().extend(
    {
        "bayer_labels": {
            "font_name": "Literata",
            "font_size": 10
        }
    }
)
```
Alternatively, you can do this:
```python
style = PlotStyle()
style.bayer_labels.font_name = "Literata"
style.bayer_labels.font_size = 10

```

### More Complex Example
The method above works well for overriding a few style properties, but if you want to create a more complex style then it's probably easier to define it in a YAML file and use PlotStyle's [`load_from_file`](reference.md#starplot.PlotStyle.load_from_file) static method.

Example:


```yaml
# style.yml

# make the Milky Way gray
milky_way:
  opacity: 0.36
  fill: '#888'

# change the color of star labels to blue and
# and change their symbol from dots to stars
star:
  label:
    fill: '#0e69b8'
  marker:
    symbol: star

# make nebulas green and their markers diamonds
dso_nebula:
  marker:
    fill: green
    symbol: diamond

```

Then, to use your new style:

```python
from starplot import PlotStyle, MapPlot

style = PlotStyle.load_from_file("style.yml")

p = MapPlot(
    ra_min=4,
    ra_max=8,
    dec_min=0,
    dec_max=20,
    style=style,
)

```

---

## Overriding Styles When Plotting

After you create a plot instance and start plotting objects, then you may want to override the plot's style sometimes. For example, you may want to plot the brightest stars with one style and the dimmer stars with a different style. Starplot provides three easy ways to do this:

### Via `style` kwarg {.mt-none}
All plotting functions have an optional `style` kwarg that lets you pass in a dictionary of any styles you want to override for that plotting call. For example, here's how you can plot bright stars with a different marker and color than the plot's style:

```python
p.stars(
    where=[_.magnitude < 3],
    style={
        "marker": {
            "symbol": "star",
            "fill": "red",
        }
    }
)
```


### Via `style__*` kwargs
When you only want to override one or two style properties, it can be tedious to create a dictionary, so Starplot also lets you specify overrides through keyword arguments that start with `style__` and separate each level by `__`. For example, we could re-write the previous example like this:

```python
p.stars(
    where=[_.magnitude < 3],
    style__marker__symbol="star",
    style__marker__fill="red",
)
```

**When overriding styles like this, you only have to define style properties you want to override.** Other properties will be inherited from the plot's style.

### Via style context manager

You can also use a context manager to temporarily override styles:

```python

with p.style.dso_open_cluster as oc:
    # make open cluster labels bigger and bolder
    oc.label.font_size *= 1.5
    oc.label.font_weight = 'heavy'
    p.open_clusters(where=[_.magnitude < 9])

# when exiting the context manager, the style will be reverted to its original value
# so, the following line will use the original style (BEFORE the context manager)
p.open_clusters(where=[_.magnitude >= 9])
```

---


<br/>
<br/>
