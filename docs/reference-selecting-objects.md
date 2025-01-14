
When plotting [stars][starplot.MapPlot.stars] or [deep sky objects (DSOs)][starplot.MapPlot.dsos], you can select exactly which objects to plot by using expressions that reference fields on the object's model. Starplot uses [Ibis](https://ibis-project.org/) for handling these expressions and filtering data from the data backend, so if you're familar with that library then you already have a head start on selecting data in Starplot.

The basic idea is that when you call `stars()` or `dsos()` you can pass a list of expressions that are used to determine which stars/DSOs are plotted. Only the stars/DSOs that satisfy ALL the conditions will be plotted.

Let's check out a simple example:

## Example

```python linenums="1" hl_lines="15-20"
from starplot import MapPlot, Projection, _

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
        _.magnitude < 12,
        _.size > 0.08,
    ]
)
```
On line 15, we plot only the DSOs we want by passing the `where` keyword argument. This argument contains a list of expressions that describe which objects you want to plot. Only the DSOs that satisfy ALL of these conditions will be plotted.

### More Expression Examples

| Expression                                       | Description                           |
| ------------------------------------------------ | ------------------------------------- |
| `_.hip.notnull()`                                | Select stars that have a HIP id                                           |
| `(_.hip.notnull()) | (_.bv < 0)`                 | Select stars that have a HIP id **OR** have a bluish color (bv < 0)       |
| `_.name.isin(["Sirius", "Rigel", "Vega"])`       | Select stars with the names Sirius, Rigel, or Vega                        |
| `(_.size.isnull()) | (_.size > 0.01)`            | Select DSOs that have no defined size **OR** are larger than 0.01 square degrees      |
| `_.geometry.intersects(m45.geometry)`            | Select stars that are within the Pleiades (M45) star cluster (assumes `m45 = DSO.get(m='45')`)     |

Starplot supports all expressions from [Ibis](https://ibis-project.org/), so check out [their documentation](https://ibis-project.org/reference/expression-generic) for more details.

## Important Details

- When writing expressions, you can reference any field on the [model](/reference-models) you're filtering
- See table below for a list of [operators](#operators) you can use in your expressions
- Each field also has [functions](#functions) available to check for null, etc
- You can combine expressions with the bitwise OR (`|`) / AND (`&`) operators, but you **must** put parenthesis around each expression when doing this (e.g. `(Star.magnitude > 8) | (Star.name == "Vega")`)

## Operators

| Operator        | Description                              | Example                              |
| :-------------:   | ---------------------------------------- | ------------------------------------ |
| `<`, `<=`       | Less than, less than or equal to         | `_.magnitude < 8`                 |
| `>`, `>=`       | Greater than, greater than or equal to   | `_.magnitude >= 2`                 |
| `==`            | Equals (handles `None` properly)         | `_.name == "Vega"`                |
| `!=`            | NOT equal (handles `None` properly)      | `_.name != "NGC1976"`              |

There are also a few operators you can use to combine expressions:

| Operator  | Description                               | Example                                            |
| :---------: | ----------------------------------------- | -------------------------------------------------- |
| `|`       | Logical OR                                | `(_.magnitude > 8) | (_.name == "Vega")`     |
| `&`       | Logical AND                               | `(_.magnitude < 8) & (_.size.is_not_null())`   |

**Important**: When using operators to combine expressions, you must put each expression in parenthesis:

```python
# Good ✅ 
(_.magnitude > 8) | (_.name == "Vega")

# Bad ❌ 
_.magnitude > 8 | _.name == "Vega"
```

<br/><br/>