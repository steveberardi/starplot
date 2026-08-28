

Below are previews of all built-in gradients available in Starplot. They're most commonly used for the axes background (e.g. to simulate the sky's color during twilight or daytime), but they can be used anywhere a fill color is accepted, including marker fills. See [`PolygonStyle`][starplot.PolygonStyle] for details on how a gradient `fill` value is rendered (including the `gradient_type` field).

<div class="gradient-swatch-grid" markdown>

<div class="gradient-swatch-card" markdown>
![Daylight](/images/reference/gradient_daylight.svg){ loading=lazy .gradient-swatch-img}

`daylight`{: .gradient-swatch-name}
</div>

<div class="gradient-swatch-card" markdown>
![Sun](/images/reference/gradient_sun.svg){ loading=lazy .gradient-swatch-img}

`sun`{: .gradient-swatch-name}
</div>

<div class="gradient-swatch-card" markdown>
![New Moon](/images/reference/gradient_new_moon.svg){ loading=lazy .gradient-swatch-img}

`new_moon`{: .gradient-swatch-name}
</div>

<div class="gradient-swatch-card" markdown>
![Bold Sunset](/images/reference/gradient_bold_sunset.svg){ loading=lazy .gradient-swatch-img}

`bold_sunset`{: .gradient-swatch-name}
</div>

<div class="gradient-swatch-card" markdown>
![Civil Twilight](/images/reference/gradient_civil_twilight.svg){ loading=lazy .gradient-swatch-img}

`civil_twilight`{: .gradient-swatch-name}
</div>

<div class="gradient-swatch-card" markdown>
![Nautical Twilight](/images/reference/gradient_nautical_twilight.svg){ loading=lazy .gradient-swatch-img}

`nautical_twilight`{: .gradient-swatch-name}
</div>

<div class="gradient-swatch-card" markdown>
![Astronomical Twilight](/images/reference/gradient_astronomical_twilight.svg){ loading=lazy .gradient-swatch-img}

`astronomical_twilight`{: .gradient-swatch-name}
</div>

<div class="gradient-swatch-card" markdown>
![True Night](/images/reference/gradient_true_night.svg){ loading=lazy .gradient-swatch-img}

`true_night`{: .gradient-swatch-name}
</div>

<div class="gradient-swatch-card" markdown>
![Pre-Dawn](/images/reference/gradient_pre_dawn.svg){ loading=lazy .gradient-swatch-img}

`pre_dawn`{: .gradient-swatch-name}
</div>

<div class="gradient-swatch-card" markdown>
![Optic Falloff](/images/reference/gradient_optic_falloff.svg){ loading=lazy .gradient-swatch-img}

`optic_falloff`{: .gradient-swatch-name}
</div>

<div class="gradient-swatch-card" markdown>
![Optic Fall In](/images/reference/gradient_optic_fall_in.svg){ loading=lazy .gradient-swatch-img}

`optic_fall_in`{: .gradient-swatch-name}
</div>

</div>

<h2>Build Your Own</h2>

A gradient is just a list of stops in the format: `(offset, color)` -- the same format used by all the built-in gradients above -- so you can define your own and use it anywhere a fill color is accepted, e.g. the axes background:

```python
from starplot import MapPlot, Miller, _
from starplot.styles import PlotStyle, extensions

# the last stop should always be at 1.0
my_gradient = [
    (0.0, "#f4d58d"),
    (0.3, "#c17ecb"),
    (0.7, "#4b3f8f"),
    (1.0, "#100d29"),
]

example_style = PlotStyle().extend(
    extensions.BLUE_NIGHT,
    extensions.MAP,
)
example_style.axes.background.fill = my_gradient

cas = Constellation.get(iau_id="cas")

p = MapPlot(
    projection=StereoNorth(center_ra=15),
    ra_min=-5,
    ra_max=35,
    dec_min=55,
    dec_max=65,
    style=example_style,
    scale=1.5,
)
p.stars(
    where=[_.hip.isin(cas.star_hip_ids)],
    where_labels=False,
    style__marker__symbol="star_4",
    style__marker__stroke_width=4,
    size_fn=lambda s: 80,
)
p.constellations()
p.export("gradient_example.svg")
```

![Example of a custom-defined gradient applied to a map plot's axes background](/images/reference/gradient_example.svg){ loading=lazy style="max-width:800px;width:100%;height:auto;margin:24px auto;display:block;" }

Most of the gradients shown above (all except `sun` and `new_moon`) are also available as ready-to-use [style extensions](extensions.md) named `GRADIENT_<NAME>` (e.g. `GRADIENT_CIVIL_TWILIGHT`), which apply the gradient directly to the axes background without having to define the stops yourself.

<br/>
<br/>
