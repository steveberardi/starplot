Starplot has models to represent some of the objects you can plot, including stars, DSOs, planets, the Sun, and the Moon. These models are used for many things in Starplot:

- Selecting objects to plot (via the `where` kwarg) ([see docs](reference-selecting-objects.md))
- Creating callables to calculate size/color/alpha values ([see docs](reference-callables.md))
- Keeping track of plotted objects (via [`ObjectList`][starplot.ObjectList])
- Getting the position of an object at a specific time (via `get()`)
- Getting a list of objects that meet a series of conditions (via `find()`)


::: starplot.Star
    options:
        inherited_members: true
        docstring_section_style: list
        show_root_heading: true
        show_docstring_attributes: true
        members_order: source


::: starplot.Constellation
    options:
        inherited_members: true
        docstring_section_style: list
        show_root_heading: true
        show_docstring_attributes: true
        members_order: source

::: starplot.DSO
    options:
        inherited_members: true
        docstring_section_style: list
        show_root_heading: true
        show_docstring_attributes: true
        members_order: source

::: starplot.models.dso.DsoType
    options:
        show_root_heading: true
        show_docstring_attributes: true
        members: true
        
::: starplot.Planet
    options:
        inherited_members: true
        docstring_section_style: list
        show_root_heading: true
        show_docstring_attributes: true
        members_order: source

::: starplot.Sun
    options:
        inherited_members: true
        docstring_section_style: list
        show_root_heading: true
        show_docstring_attributes: true
        members_order: source

::: starplot.Moon
    options:
        inherited_members: true
        docstring_section_style: list
        show_root_heading: true
        show_docstring_attributes: true
        members_order: source

::: starplot.ObjectList
    options:
        inherited_members: true
        docstring_section_style: list
        show_root_heading: true
        show_docstring_attributes: true
        members_order: source