Callables allow you to define your own functions for calculating a few of the style properties for stars: size, alpha (opacity), and color. Starplot has a few basic callables built-in, but you can also create your own!

???- tip "What's a Callable?"

    In Python, a "callable" is anything that can be "called" — e.g. a function or a class with `__call__` implemented.


## Example

Here's a basic example of using one of the built-in callables to colorize the stars based on their BV index:

```python
from starplot.styles import PlotStyle, extensions
from starplot.map import Projection

import starplot as sp

style = PlotStyle().extend(
    extensions.GRAYSCALE_DARK,
    extensions.MAP,
)
p = sp.MapPlot(
    projection=Projection.MERCATOR,
    ra_min=3.4,
    ra_max=8,
    dec_min=-16,
    dec_max=25.6,
    style=style,
    resolution=2600,
)
p.plot_stars(
    limiting_magnitude=12,
    color_fn=sp.callables.color_by_bv
)
p.plot_dsos(
    limiting_magnitude=12,
    plot_null_magnitudes=True,
)
p.plot_constellations()

p.export("orion_colored_stars.png", padding=0.25)
```



## Built-In Callables

All of these are importable from `starplot.callables`

### ::: starplot.callables
    options:
        inherited_members: true
        merge_init_into_class: true
        <!-- show_root_heading: false -->
        docstring_section_style: list
        <!-- separate_signature: true -->
