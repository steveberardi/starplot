# Styling Framework

Starplot has a styling framework that lets you fully customize the appearance of your plots. The framework consists of a bunch of [Pydantic models](https://docs.pydantic.dev/latest/usage/models/) that represent different things you can style (e.g. markers, lines, labels, etc). Since they're based on Pydantic models, this means you can define new styles through Python code, a JSON, or even a YAML file.

- [Basic Usage](#basic-usage)
- [Creating a Style](#creating-a-style)
- [Extending a Style](#extending-a-style)
- [Overriding a Style at plot time](#overriding-styles-when-plotting)
- [Built-in Style Extensions](#built-in-style-extensions)
- [Code Reference](#code-reference)


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
style.star.marker.color = "red"
style.star.label.font_size = 20
```

This works well when you only want to change a couple properties, but for more complex styling it's easier to use PlotStyle's `extend` method which is explained in the next section.

## Extending a Style

Once you have an instance of a PlotStyle, then you can customize it with the PlotStyle's [`extend`](#starplot.PlotStyle.extend) method. This method takes in one or more args of dictionaries and applies them to the original style in sequential order. In other words, when extending a PlotStyle, **you only have to define style properties that you want to override from the current style** — similar to how Cascading Style Sheets (CSS) work.

Starplot has a few [built-in extensions](#style-extensions) for applying color schemes and optimizing different plot types. But, you can also easily create your own extensions.

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
The method above works well for overriding a few style properties, but if you want to create a more complex style then it's probably easier to define it in a YAML file and use PlotStyle's [`load_from_file`](#starplot.PlotStyle.load_from_file) static method.

Example:


```yaml
# style.yml

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
    symbol: star

# make nebulas green and their markers diamonds
dso_nebula:
  marker:
    color: green
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

After you create a plot instance and start plotting stuff (e.g. stars, DSOs, etc), then you may want to override the plot's style sometimes. For example, you may want to plot the brightest stars with one style and the dimmer stars with a different style (see the example [map of Sagittarius](/examples/map-sagittarius/) which uses different markers for brighter stars). Starplot provides two easy ways to do this:

### Via `style` kwarg {.mt-none}
All plotting functions have an optional `style` kwarg that lets you pass in a dictionary of any styles you want to override for that plotting call. For example, here's how you can plot bright stars with a different marker and color than the plot's style:

    ```python
    p.stars(
        where=[_.magnitude < 3],
        style={
            "marker": {
                "symbol": "star",
                "color": "red",
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
        style__marker__color="red",
    )
    ```

**When overriding styles like this, you only have to define style properties you want to override.** Other properties will be inherited from the plot's style.

### Via style context manager

!!! example "Experimental"

    This is currently an "experimental" feature, which means it's likely to be changed and improved in upcoming versions of Starplot.
    It also means the feature likely has limitations.

    **Help us improve this feature by submitting feedback on [GitHub (open an issue)](https://github.com/steveberardi/starplot/issues) or chat with us on [Discord](https://discord.gg/WewJJjshFu). Thanks!**

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

## Style Extensions

Starplot has many built-in style extensions for different color schemes, plot types, and gradient backgrounds.

Using them is pretty simple:

```python
from starplot import styles

style = styles.PlotStyle().extend(
    styles.extensions.BLUE_GOLD,
    styles.extensions.GRADIENT_PRE_DAWN,
)
```

- **Color Schemes**
    - `GRAYSCALE` - Optimized for printing in grayscale ([details](#extensions-grayscale))
    - `GRAYSCALE_DARK` - Like `GRAYSCALE`, but inverted (white stars, black background) ([details](#extensions-grayscale-dark))
    - `BLUE_LIGHT` - Light and bright colors ([details](#extensions-blue-light))
    - `BLUE_MEDIUM` - Medium brightness bluish gray colors ([details](#extensions-blue-medium))
    - `BLUE_DARK` - Dark "Starplot blue" colors ([details](#extensions-blue-dark))
    - `BLUE_GOLD` - Dark blue / gold colors ([details](#extensions-blue-gold))
    - `BLUE_NIGHT` - Very dark blue background with colored markers ([details](#extensions-blue-night))
    - `ANTIQUE` - Antique map inspired colors ([details](#extensions-antique))
    - `NORD` - Nord-inspired colors ([details](#extensions-nord))
- **Plot types**
    - `OPTIC` - Basic styling tailored for optic plots ([details](#extensions-optic))
    - `MAP` - Basic styling tailored for map plots ([details](#extensions-map))
- **Gradients**
    - `GRADIENT_DAYLIGHT`
    - `GRADIENT_BOLD_SUNSET`
    - `GRADIENT_CIVIL_TWILIGHT`
    - `GRADIENT_NAUTICAL_TWILIGHT`
    - `GRADIENT_ASTRONOMICAL_TWILIGHT`
    - `GRADIENT_TRUE_NIGHT`
    - `GRADIENT_PRE_DAWN`
    - `GRADIENT_OPTIC_FALLOFF`
    - `GRADIENT_OPTIC_FALL_IN`

<!-- GRAYSCALE -->
<h2 class="doc doc-heading" id="extensions-grayscale"><code>GRAYSCALE</code></h2>

<div class="indent" markdown>
Optimized for printing in grayscale

???- star "Source"

    ```yaml 
    --8<-- "src/starplot/styles/ext/grayscale.yml"
    ```
</div>

<!-- GRAYSCALE DARK -->
<h2 class="doc doc-heading" id="extensions-grayscale-dark"><code>GRAYSCALE_DARK</code></h2>

<div class="indent" markdown>
Like `GRAYSCALE`, but inverted (white stars, black background)

???- star "Source"

    ```yaml
    --8<-- "src/starplot/styles/ext/grayscale_dark.yml"
    ```
</div>

<!-- BLUE LIGHT -->
<h2 class="doc doc-heading" id="extensions-blue-light"><code>BLUE_LIGHT</code></h2>

<div class="indent" markdown>
Light and bright colors

???- star "Source"

    ```yaml
    --8<-- "src/starplot/styles/ext/blue_light.yml"
    ```
</div>

<!-- BLUE MEDIUM -->
<h2 class="doc doc-heading" id="extensions-blue-medium"><code>BLUE_MEDIUM</code></h2>

<div class="indent" markdown>
Medium brightness bluish gray colors

???- star "Source"

    ```yaml 
    --8<-- "src/starplot/styles/ext/blue_medium.yml"
    ```
</div>

<!-- BLUE DARK -->
<h2 class="doc doc-heading" id="extensions-blue-dark"><code>BLUE_DARK</code></h2>

<div class="indent" markdown>
Dark bluish gray colors

???- star "Source"

    ```yaml 
    --8<-- "src/starplot/styles/ext/blue_dark.yml"
    ```
</div>

<!-- BLUE GOLD -->
<h2 class="doc doc-heading" id="extensions-blue-gold"><code>BLUE_GOLD</code></h2>

<div class="indent" markdown>
Dark bluish gold colors

???- star "Source"

    ```yaml 
    --8<-- "src/starplot/styles/ext/blue_gold.yml"
    ```
</div>

<!-- BLUE NIGHT -->
<h2 class="doc doc-heading" id="extensions-blue-night"><code>BLUE_NIGHT</code></h2>

<div class="indent" markdown>
Very dark blue background with colored markers

???- star "Source"

    ```yaml 
    --8<-- "src/starplot/styles/ext/blue_night.yml"
    ```
</div>

<!-- ANTIQUE -->
<h2 class="doc doc-heading" id="extensions-antique"><code>ANTIQUE</code></h2>

<div class="indent" markdown>
Antique map inspired colors

???- star "Source"

    ```yaml 
    --8<-- "src/starplot/styles/ext/antique.yml"
    ```
</div>

<!-- NORD -->
<h2 class="doc doc-heading" id="extensions-nord"><code>NORD</code></h2>

<div class="indent" markdown>
Nord inspired colors

???- star "Source"

    ```yaml 
    --8<-- "src/starplot/styles/ext/nord.yml"
    ```
</div>

<!-- OPTIC -->
<h2 class="doc doc-heading" id="extensions-optic"><code>OPTIC</code></h2>

<div class="indent" markdown>
Basic styling tailored for optic plots

???- star "Source"

    ```yaml 
    --8<-- "src/starplot/styles/ext/optic.yml"
    ```
</div>

<!-- MAP -->
<h2 class="doc doc-heading" id="extensions-map"><code>MAP</code></h2>

<div class="indent" markdown>
Basic styling tailored for map plots

???- star "Source"

    ```yaml 
    --8<-- "src/starplot/styles/ext/map.yml"
    ```
</div>

    
---

## Code Reference

::: starplot.PlotStyle
    options:
        show_root_heading: true
        show_docstring_attributes: true
        separate_signature: true
        show_signature_annotations: true
        signature_crossrefs: true
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

::: starplot.styles.ArrowStyle
    options:
        show_root_heading: true
        show_docstring_attributes: true
        inherited_members: true

---

::: starplot.styles.ObjectStyle
    options:
        show_root_heading: true
        show_docstring_attributes: true

::: starplot.styles.PathStyle
    options:
        show_root_heading: true
        show_docstring_attributes: true

::: starplot.styles.LegendStyle
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

::: starplot.styles.LegendLocationEnum
    options:
        show_root_heading: true
        show_docstring_attributes: true
        members: true

::: starplot.styles.AnchorPointEnum
    options:
        show_root_heading: true
        show_docstring_attributes: true
        members: true

::: starplot.styles.CapStyleEnum
    options:
        show_root_heading: true
        show_docstring_attributes: true
        members: true

::: starplot.styles.JoinStyleEnum
    options:
        show_root_heading: true
        show_docstring_attributes: true
        members: true

::: starplot.styles.ZOrderEnum
    options:
        show_root_heading: true
        show_docstring_attributes: true
        members: true

---

<br/>
<br/>
