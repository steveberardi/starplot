# Gradients

All styles with a `fill` property can be filled as a solid color or a gradient. Starplot has a few built-in gradient styles, but you can also [build your own](#build-your-own).

Below are previews of all built-in gradients available in Starplot. They're most commonly used for the axes background (e.g. to simulate the sky's color during twilight or daytime), but they can be used anywhere a fill color is accepted, including marker fills. Each one is a tuple of `(offset, color)` stops -- the same shape as [`GradientStyle.stops`][starplot.GradientStyle] -- so most are available directly as ready-to-use [style extensions](extensions.md) (see below), or you can wrap one yourself: `GradientStyle(stops=gradients.CIVIL_TWILIGHT, type="linear")`. See [`PolygonStyle`][starplot.PolygonStyle] for details on how a gradient `fill` value is rendered.

<div class="gradient-swatch-grid" markdown>

<div class="gradient-swatch-card" markdown>
![Daylight](/images/reference/gradient_daylight.svg){ loading=lazy .gradient-swatch-img}

`DAYLIGHT`{: .gradient-swatch-name}
</div>

<div class="gradient-swatch-card" markdown>
![Sun](/images/reference/gradient_sun.svg){ loading=lazy .gradient-swatch-img}

`SUN`{: .gradient-swatch-name}
</div>

<div class="gradient-swatch-card" markdown>
![New Moon](/images/reference/gradient_new_moon.svg){ loading=lazy .gradient-swatch-img}

`NEW_MOON`{: .gradient-swatch-name}
</div>

<div class="gradient-swatch-card" markdown>
![Bold Sunset](/images/reference/gradient_bold_sunset.svg){ loading=lazy .gradient-swatch-img}

`BOLD_SUNSET`{: .gradient-swatch-name}
</div>

<div class="gradient-swatch-card" markdown>
![Civil Twilight](/images/reference/gradient_civil_twilight.svg){ loading=lazy .gradient-swatch-img}

`CIVIL_TWILIGHT`{: .gradient-swatch-name}
</div>

<div class="gradient-swatch-card" markdown>
![Nautical Twilight](/images/reference/gradient_nautical_twilight.svg){ loading=lazy .gradient-swatch-img}

`NAUTICAL_TWILIGHT`{: .gradient-swatch-name}
</div>

<div class="gradient-swatch-card" markdown>
![Astronomical Twilight](/images/reference/gradient_astronomical_twilight.svg){ loading=lazy .gradient-swatch-img}

`ASTRONOMICAL_TWILIGHT`{: .gradient-swatch-name}
</div>

<div class="gradient-swatch-card" markdown>
![True Night](/images/reference/gradient_true_night.svg){ loading=lazy .gradient-swatch-img}

`TRUE_NIGHT`{: .gradient-swatch-name}
</div>

<div class="gradient-swatch-card" markdown>
![Pre-Dawn](/images/reference/gradient_pre_dawn.svg){ loading=lazy .gradient-swatch-img}

`PRE_DAWN`{: .gradient-swatch-name}
</div>

<div class="gradient-swatch-card" markdown>
![Optic Falloff](/images/reference/gradient_optic_falloff.svg){ loading=lazy .gradient-swatch-img}

`OPTIC_FALLOFF`{: .gradient-swatch-name}
</div>

<div class="gradient-swatch-card" markdown>
![Optic Fall In](/images/reference/gradient_optic_fall_in.svg){ loading=lazy .gradient-swatch-img}

`OPTIC_FALL_IN`{: .gradient-swatch-name}
</div>

</div>

<h2 id="build-your-own">Build Your Own</h2>

You can define your own gradient by setting the `fill` of a style to an instance of [`GradientStyle`][starplot.styles.GradientStyle]. The `GradientStyle` consists of a tuple of color stops (in the format of `(offset, color)`) and a `type` (`"linear"` or `"radial"`).

Example:
<div class="tutorial">
```python
--8<-- "examples/gradient.py"
```
</div>

![Example of a custom-defined gradient applied to a map plot's axes background](/images/examples/gradient.svg){ loading=lazy style="max-width:800px;width:100%;height:auto;margin:24px auto;display:block;" }

Most of the gradients shown above (all except `sun` and `new_moon`) are also available as ready-to-use [style extensions](extensions.md) named `GRADIENT_<NAME>` (e.g. `GRADIENT_CIVIL_TWILIGHT`), which apply the gradient directly to the axes background without having to define the stops yourself.

<br/>
<br/>
