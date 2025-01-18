Callables allow you to define your own functions for calculating a few of the style properties for stars: size, alpha (opacity), color, and the star's label. DSOs support callables for alpha and labels only. Starplot has a few basic callables built-in, but you can also create your own.

???- tip "What's a Callable?"

    In Python, a "callable" is anything that can be "called" — e.g. a function or a class with `__call__` implemented.

    As a simple example, here's how you can pass a callable to Python's `sorted` function to sort a list of strings by their length:
    ```python

    >>> animals = ["elephant","cat", "dog", "tiger"]

    >>> sorted(animals, key=lambda a: len(a))
    
    ['cat', 'dog', 'tiger', 'elephant']
    
    ```
    
    In the example above, the value of `key` is the callable — in this case, a lambda function.

    Here's another way to write the code above:

    ```python

    >>> animals = ["elephant","cat", "dog", "tiger"]

    >>> def length(a):
    ...   return len(a)
    ...
    >>> sorted(animals, key=length)
    
    ['cat', 'dog', 'tiger', 'elephant']
    
    ```


## Example

Here's a basic example of using one of the built-in callables to colorize the stars based on their BV index:

```python hl_lines="18"
from starplot import MapPlot, Projection, _
from starplot.styles import PlotStyle, extensions

style = PlotStyle().extend(
    extensions.GRAYSCALE_DARK,
    extensions.MAP,
)
p = MapPlot(
    projection=Projection.MERCATOR,
    ra_min=3.4,
    ra_max=8,
    dec_min=-16,
    dec_max=25.6,
    style=style,
)
p.stars(
    where=[_.magnitude < 12],
    color_fn=callables.color_by_bv, # <-- here's where we specify the callable
)
p.constellations()

p.export("orion_colored_stars.png")
```

## Creating Your Own Callable
Let's say you wanted to create a plot where the stars brighter than magnitude 4 should be colored blue and stars dimmer than that should be colored red. Here's a way to do that with a custom callable:

```python
# first we define the callable:
def color_by_mag(star: Star) -> str:
    if star.magnitude <= 4:
        return "#218fef"
    else:
        return "#d52727"

# then to use your callable:
p = MapPlot(...)
p.stars(
    where=[_.magnitude < 12],
    color_fn=color_by_mag,
)
```
Every callable for stars is passed an instance of [`Star`][starplot.Star], so you can reference various properties of stars in your callables. Similarly, every callable for a DSO is passed an instance of [`DSO`][starplot.DSO].

## Built-In Callables

All of these are importable from `starplot.callables`

### ::: starplot.callables
    options:
        inherited_members: true
        merge_init_into_class: true
        <!-- show_root_heading: false -->
        docstring_section_style: list
        <!-- separate_signature: true -->
