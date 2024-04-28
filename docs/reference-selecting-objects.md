When plotting [stars][starplot.MapPlot.stars] or [deep sky objects (DSOs)][starplot.MapPlot.dsos], you may want to limit the plotted objects by more than just a limiting magnitude. Starplot provides a way to filter stars/DSOs by using expressions. The syntax is inspired by the filtering methods of [Polars](https://docs.pola.rs/py-polars/html/reference/dataframe/api/polars.DataFrame.filter.html), [Peewee](https://docs.peewee-orm.com/en/latest/peewee/querying.html#filtering-records), and many other popular ORMs, so if you're familiar with those libraries then you already have a head start on Starplot's version.

The basic idea is that when you call `stars()` or `dsos()` you can pass a list of expressions that are used to determine which stars/DSOs are plotted. Only the stars/DSOs that satisfy ALL the conditions will be plotted.

Let's check out a simple example:

## Example

```python linenums="1" hl_lines="16-21"
from starplot import MapPlot, Projection
from starplot.models import DSO

# Create a simple map around Orion
p = MapPlot(
    projection=Projection.MERCATOR,
    ra_min=3.4,
    ra_max=8,
    dec_min=-16,
    dec_max=25.6,
)

# Plot all DSOs that satisfy two conditions:
#   1. Magnitude is less than 12
#   2. Size is greater than 0.08
p.dsos(
    where=[
        DSO.magnitude < 12,
        DSO.size > 0.08,
    ]
)
```
On line 16, we plot only the DSOs we want by passing the `where` keyword argument. This argument contains a list of expressions that describe which objects you want to plot. Only the DSOs that satisfy ALL of these conditions will be plotted.

### More Expression Examples

| Expression                                       | Description                           |
| ------------------------------------------------ | ------------------------------------- |
| `Star.hip.is_not_null()`                         | Select stars that have a HIP id                                           |
| `(Star.hip.is_not_null()) | (Star.bv < 0)`       | Select stars that have a HIP id **OR** have a bluish color (bv < 0)       |
| `Star.name.is_in(["Sirius", "Rigel", "Vega"])`   | Select stars with the names Sirius, Rigel, or Vega                        |
| `(DSO.size.is_null()) | (DSO.size > 0.01)`       | Select DSOs that have no defined size **OR** are larger than 0.01 square degrees      |

## Important Details

- When writing expressions, you can reference any field on the [model](/reference-models) you're filtering
- See table below for a list of [operators](#operators) you can use in your expressions
- Each field also has [functions](#functions) available to check for null, etc
- You can combine expressions with the bitwise OR (`|`) / AND (`&`) operators, but you **must** put parenthesis around each expression when doing this (e.g. `(Star.magnitude > 8) | (Star.name == "Vega")`)

## Operators

| Operator        | Description                              | Example                              |
| :-------------:   | ---------------------------------------- | ------------------------------------ |
| `<`, `<=`       | Less than, less than or equal to         | `Star.magnitude < 8`                 |
| `>`, `>=`       | Greater than, greater than or equal to   | `DSO.magnitude >= 2`                 |
| `==`            | Equals (handles `None` properly)         | `Star.name == "Vega"`                |
| `!=`            | NOT equal (handles `None` properly)      | `DSO.name != "NGC1976"`              |

There are also a few operators you can use to combine expressions:

| Operator  | Description                               | Example                                            |
| :---------: | ----------------------------------------- | -------------------------------------------------- |
| `|`       | Logical OR                                | `(Star.magnitude > 8) | (Star.name == "Vega")`     |
| `&`       | Logical AND                               | `(DSO.magnitude < 8) & (DSO.size.is_not_null())`   |

**Important**: When using operators to combine expressions, you must put each expression in parenthesis:

```python
# Good ✅ 
(Star.magnitude > 8) | (Star.name == "Vega")

# Bad ❌ 
Star.magnitude > 8 | Star.name == "Vega"
```

## Functions

### ::: starplot.models.base.Term
    options:
        inherited_members: true
        docstring_section_style: list
        show_root_heading: false
        show_docstring_attributes: true
        members_order: source
        show_root_toc_entry: false
