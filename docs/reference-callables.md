# Callables

Many functions in Starplot allow you to pass a callable for creating dynamic styles and labels for objects. For example, when you plot stars you can optionally specify a callable for determining the size of each star. Starplot has a few basic callables built-in, but you can also create your own.

- Built-In Callables: [Size](#size), [Color](#color), [Labels](#labels)

- [Creating your own callable](#creating-your-own-callable)

- _[See chapter 8 of the tutorial for an example of using a callable :material-arrow-right:](/tutorial/08/)_


???- tip  "What's a Callable?"

    In Python, a "callable" is anything that can be "called" (e.g. a function or a class with `__call__` implemented).

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

<div class="divider"></div>

## Size

### ::: starplot.callables.size_by_magnitude
    options:
        inherited_members: true
        merge_init_into_class: true
        show_root_heading: true
        show_source: true

### ::: starplot.callables.size_by_magnitude_galaxy
    options:
        inherited_members: true
        merge_init_into_class: true
        show_root_heading: true
        show_source: true

### ::: starplot.callables.size_by_fov_factory
    options:
        inherited_members: true
        merge_init_into_class: true
        show_root_heading: true
        show_source: true

<div class="divider"></div>

## Color

### ::: starplot.callables.color_by_bv
    options:
        inherited_members: true
        merge_init_into_class: true
        show_root_heading: true
        show_source: true

### ::: starplot.callables.color_by_bv_gradient
    options:
        inherited_members: true
        merge_init_into_class: true
        show_root_heading: true
        show_source: true

<div class="divider"></div>

## Labels

### ::: starplot.callables.floor_hours_label
    options:
        inherited_members: true
        merge_init_into_class: true
        show_root_heading: true
        show_source: true

### ::: starplot.callables.rounded_degrees_label
    options:
        inherited_members: true
        merge_init_into_class: true
        show_root_heading: true
        show_source: true

### ::: starplot.callables.azimuth_with_cardinal_direction_label_factory
    options:
        inherited_members: true
        merge_init_into_class: true
        show_root_heading: true
        show_source: true

<div class="divider"></div>

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


<br/><br/><br/>
