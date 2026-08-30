# Color

Anywhere a style has a color property — a marker's fill, a line's stroke, a label's text or halo, a legend's background, etc — that property is defined by Starplot's `Color` type. `Color` follows the [CSS3 color specification](http://www.w3.org/TR/css3-color/#svg-color), so you can define colors the same way you would in CSS: by name, hex code, `rgb()`/`rgba()`, or `hsl()`/`hsla()`. It also supports an alpha channel, so any of these formats can have a transparency level.

- [Supported Formats](#supported-formats)
- [Basic Usage](#basic-usage)
- [Transparency](#transparency)
- [Null Values](#null-values)

## Supported Formats

<div class="color-swatch-grid" markdown>

<!-- <div class="color-swatch-card" markdown>
<div class="color-swatch-preview"><span style="background-color: aliceblue;"></span></div>

`"aliceblue"`{: .color-swatch-name}
</div> -->

<div class="color-swatch-card" markdown>
<div class="color-swatch-preview"><span style="background-color: steelblue;"></span></div>

`"steelblue"`{: .color-swatch-name}
</div>
<!-- 
<div class="color-swatch-card" markdown>
<div class="color-swatch-preview"><span style="background-color: #888;"></span></div>

`"#888"`{: .color-swatch-name}
</div> -->

<div class="color-swatch-card" markdown>
<div class="color-swatch-preview"><span style="background-color: #ebbdd4;"></span></div>

`"#ebbdd4"`{: .color-swatch-name}
</div>

<div class="color-swatch-card" markdown>
<div class="color-swatch-preview"><span style="background-color: rgb(89, 120, 155);"></span></div>

`"rgb(89, 120, 155)"`{: .color-swatch-name}
</div>

<div class="color-swatch-card" markdown>
<div class="color-swatch-preview"><span style="background-color: rgba(31, 132, 214, 0.6);"></span></div>

`"rgba(31, 132, 214, 0.6)"`{: .color-swatch-name}
</div>

<div class="color-swatch-card" markdown>
<div class="color-swatch-preview"><span style="background-color: hsl(203, 60%, 84%);"></span></div>

`"hsl(203, 60%, 84%)"`{: .color-swatch-name}
</div>

<div class="color-swatch-card" markdown>
<div class="color-swatch-preview"><span style="background-color: hsla(37, 78%, 80%, 0.5);"></span></div>

`"hsla(37, 78%, 80%, 0.5)"`{: .color-swatch-name}
</div>

<div class="color-swatch-card" markdown>
<div class="color-swatch-preview"><span style="background-color: rgb(201, 240, 178);"></span></div>

`(201, 240, 178)`{: .color-swatch-name}
</div>

<div class="color-swatch-card" markdown>
<div class="color-swatch-preview"><span style="background-color: rgba(250, 168, 209, 0.4);"></span></div>

`(250, 168, 209, 0.4)`{: .color-swatch-name}
</div>

</div>

<div class="color-format-table" markdown>

| Format | Examples | Description |
| ----- | ------ | --- |
| Name | `"aliceblue"`<br>`"steelblue"` | Any of the standard [CSS3 named colors](http://www.w3.org/TR/css3-color/#svg-color), case-insensitive |
| Hex | `"#888"`<br>`"#faa8d1"`<br>`"#b979b780"` | Short or long form, with or without the alpha channel |
| RGB / RGBA | `"rgb(89, 120, 155)"`<br>`"rgba(31, 132, 214, 0.6)"` | Standard CSS `rgb()`/`rgba()` function notation |
| HSL / HSLA | `"hsl(203, 60%, 84%)"`<br>`"hsla(37, 78%, 80%, 0.5)"` | Standard CSS `hsl()`/`hsla()` function notation |
| Tuple | `(201, 240, 178)`<br>`(250, 168, 209, 0.4)` | Tuple of integers (`(r, g, b)`) with values 0-255, or `(r, g, b, a)` with alpha as a `float` between `0` and `1` |
| `"transparent"` | `"transparent"` | A fully transparent color (i.e. `alpha = 0`) |

</div>

## Basic Usage

Any style property typed as `Color` will accept a value in any of the formats above, and Starplot will automatically parse and validate it:

```python
from starplot import PlotStyle

style = PlotStyle()

style.star.marker.fill = "red"
style.star.marker.fill = "#ff0000"
style.star.marker.fill = "rgb(255, 0, 0)"
style.star.marker.fill = "hsl(0, 100%, 50%)"
style.star.marker.fill = (255, 0, 0)
```

You can also create a `Color` instance directly and use its conversion methods (`as_hex()`, `as_rgb()`, `as_hsl()`) to inspect or convert a color:

```python
from starplot.styles import Color

c = Color("cornflowerblue")
c.as_hex()  # '#6495ed'
c.as_rgb()  # 'rgb(100, 149, 237)'
c.as_hsl()  # 'hsl(219, 79%, 66%)'
```

## Transparency

Every color format above supports an alpha channel, which controls the color's transparency. The alpha channel can have a value between 0 (fully transparent) to 1 (fully solid, no transparency). For example, here's how you would specify the Milky Way's fill to be 30% full:

```python
style.milky_way.fill = "rgba(200, 200, 255, 0.3)"
```

This alpha value is different from the `opacity` property that many styles also have (e.g. [`MarkerStyle.opacity`][starplot.MarkerStyle], [`PolygonStyle.opacity`][starplot.PolygonStyle]), which controls the transparency of the *entire element* (fill, stroke, everything). If you set both, they combine — e.g. a color with 50% alpha on an element with 50% opacity will render at 25% total opacity.

## Null Values

Some style properties allow `None` to mean "no color" (e.g. no stroke, no fill). For example, this removes the `stroke` around `star` markers:

```python
style.star.marker.stroke = None
```

<br/><br/><br/>
