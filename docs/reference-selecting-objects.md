
When plotting [stars][starplot.MapPlot.stars], [constellations][starplot.MapPlot.constellations], or [deep sky objects (DSOs)][starplot.MapPlot.dsos], you can select exactly which objects to plot by using expressions that reference fields on the object's model. Only the objects that satisfy ALL the conditions will be plotted.

Starplot uses [Ibis](https://ibis-project.org/) for handling these expressions, so if you're familar with that library then you already have a head start on selecting data in Starplot.

Let's check out a simple example:

<div class="tutorial">
```python linenums="1" hl_lines="15-20"
from starplot import MapPlot, Projection, _

# Create a simple map around Orion
p = MapPlot(
    projection=Projection.MERCATOR,
    ra_min=3 * 15,
    ra_max=8 * 15,
    dec_min=-16,
    dec_max=25,
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
</div>
On line 15, we plot only the DSOs we want by passing the `where` keyword argument. This argument contains a list of expressions that describe which objects you want to plot. Only the objects that satisfy ALL of these conditions will be plotted. In this example, we plot all DSOs that have a magnitude less than 12 AND a size greater than 0.08 square degrees.

When building expressions, you use the underscore, `_`, to reference fields on the model. This is kind of a ["magic variable" in Ibis (known as the Underscore API)](https://ibis-project.org/how-to/analytics/chain_expressions) which makes it easy to work with data and chain expressions together.

### More Expression Examples

Select stars that have a non-null HIP id:

    _.hip.notnull()

<hr/>
Select stars that have a HIP id **OR** have a bluish color (bv < 0):

    (_.hip.notnull()) | (_.bv < 0)

<hr/>
Select stars with the names Sirius, Rigel, or Vega:

    _.name.isin(["Sirius", "Rigel", "Vega"])

<hr/>
Select DSOs that have no defined size **OR** are larger than 0.01 square degrees:

    (_.size.isnull()) | (_.size > 0.01)

<hr/>
Select stars that are within the Pleiades (M45) star cluster (assumes `m45 = DSO.get(m='45')`):

    _.geometry.intersects(m45.geometry)

!!! star "But wait, there's more!"

    Starplot supports all expressions from <a href="https://ibis-project.org/" target="_blank">Ibis</a>, so check out <a href="https://ibis-project.org/reference/expression-generic" target="_blank">their documentation :arrow_upper_right:</a> for more details.

## Important Details

- When writing expressions, you can reference any field on the [model](/reference-models) you're filtering
- See table below for a list of [operators](#operators) you can use in your expressions
- You can combine expressions with the bitwise OR (`|`) / AND (`&`) operators, but you **must** put parenthesis around each expression when doing this (e.g. `(_.magnitude > 8) | (_.name == "Vega")`)

## Operators

| Operator          | Description                                    | Example                  |
| :-------------:   | ---------------------------------------------- | ------------------------ |
| `<`, `<=`         | Less than, less than or equal to               | `_.magnitude < 8`        |
| `>`, `>=`         | Greater than, greater than or equal to         | `_.magnitude >= 2`       |
| `==`              | Equals                                         | `_.name == "Vega"`       |
| `!=`              | NOT equal                                      | `_.name != "NGC1976"`    |

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

## Using SQL

All functions that accept a `where` list of filters _also_ have a `sql` keyword argument that lets you write a SQL query to select objects. You can also use a combination of `where` filters and a `sql` query, but the filters in `where` will be executed _first_. The table name is always an underscore: `_`.

For example, if you want to find all stars with a magnitude less than 4, you can do:

```python

bright_stars = Star.find(sql="select * from _ where magnitude < 4")

```

<br/><br/>