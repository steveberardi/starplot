When plotting stars or deep sky objects (DSOs), you may want to limit the plotted objects by more than just a limiting magnitude. Starplot provides a way to filter stars/DSOs by using expressions.

## Example


```python
p = sp.MapPlot(
    projection=Projection.MERCATOR,
    ra_min=3.4,
    ra_max=8,
    dec_min=-16,
    dec_max=25.6,
)

p.dsos(
    where=[
        (DSO.magnitude.is_null()) | (DSO.magnitude < 12),
        DSO.size.is_not_null(),
        DSO.size > 0.08,
    ]
)

```

## Operators

| Operator        | Description                              | Example                              |
| -------------   | ---------------------------------------- | ------------------------------------ |
| `<`, `<=`       | Less than, less than or equal to         | `Star.magnitude < 8`                 |
| `>`, `>=`       | Greater than, greater than or equal to   | `DSO.magnitude >= 2`                 |
| `==`            | Equals (handles `None` properly)         | `Star.name == "Vega"`                |
| `!=`            | NOT equal (handles `None` properly)      | `DSO.name != "NGC1976"`              |

There are also a few operators you can use to combine expressions:

| Operator  | Description                               | Example                                            |
| --------- | ----------------------------------------- | -------------------------------------------------- |
| `|`       | Logical OR                                | `(Star.magnitude > 8) | (Star.name == "Vega")`     |
| `&`       | Logical AND                               | `(DSO.magnitude < 8) & (DSO.size.is_not_null())`  |

!!! star "Important"
    When using operators to combine expressions, you must put each predicate in parenthesis.

## Functions

::: starplot.models.Term
    options:
        inherited_members: true
        docstring_section_style: list
        show_root_heading: false
        show_docstring_attributes: true
        members_order: source