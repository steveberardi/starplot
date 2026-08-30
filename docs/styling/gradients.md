# Gradients

Markers and polygons can have a [solid color fill](color.md) or a gradient fill. Starplot has a few pre-defined gradients, but you can also [build your own](#build-your-own). Gradient backgrounds are defined through a [`GradientStyle`][starplot.styles.GradientStyle]. The `GradientStyle` consists of a tuple of color stops (in the format of `(offset, color)`) and a `type` (`"linear"` or `"radial"`).

Pre-defined gradient stops available in `starplot.styles.gradients`:
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
![Lavender Twilight](/images/reference/gradient_lavender_twilight.svg){ loading=lazy .gradient-swatch-img}

`LAVENDER_TWILIGHT`{: .gradient-swatch-name}
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

<h2 id="using-built-in-gradients">Using Built-In Gradients</h2>

- [Example of using gradient on horizon plot](/examples/horizon-gradient/)
- [Example of using a gradient on a polygon](/examples/optic-solar-eclipse/)
- [Example of using gradients on stars](/examples/optic-m45/)

<h2 id="build-your-own">Building Your Own</h2>

You can define your own gradient by setting the `fill` of a marker or polygon style to an instance of [`GradientStyle`][starplot.styles.GradientStyle]. The `GradientStyle` consists of a tuple of color stops (in the format of `(offset, color)`) and a `type` (`"linear"` or `"radial"`).

Example:
<div class="tutorial">
```python
--8<-- "examples/gradient.py"
```
</div>

![Example of a custom-defined gradient applied to a map plot's axes background](/images/examples/gradient.svg){ loading=lazy style="max-width:800px;width:100%;height:auto;margin:24px auto;display:block;" }

<br/>
<br/>
