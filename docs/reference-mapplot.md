**Map plots are general purpose maps of the sky.** They're not dependent on an observer's location, but they are dependent on time if you want to include the planets and/or the moon in the plot.

There are four supported projections for map plots: 

- Mercator (the default)
- Stereographic North
- Stereographic South
- Mollweide

::: starplot.MapPlot
    options:
        inherited_members: true
        merge_init_into_class: true
        show_root_heading: true
        docstring_section_style: list
        <!-- separate_signature: true -->

::: starplot.Projection
    options:
        show_root_heading: true
        show_docstring_attributes: true

::: starplot.map.DEFAULT_FOV_STYLE
    options:
        show_root_heading: true
        show_docstring_attributes: true
