**Optic plots simulate what you'll see through an optic (e.g. binoculars, telescope, camera) at a specific time and place**. The simulated view will show you the true field of view for the optic, and it will even orient the stars based on the location you specify and the most logical position of your optic (in other words, it won't orient the optic to look upside down over the zenith).

These plots use an [azimuthal equidistant projection](https://en.wikipedia.org/wiki/Azimuthal_equidistant_projection), with the projection's center set to the target's position (in azimuth, altitude coordinates). This projection was chosen because it preserves the correct proportional distances from the center point.

::: starplot.OpticPlot
    options:
        inherited_members: true
        merge_init_into_class: true
        show_root_heading: true
        docstring_section_style: list

## ::: starplot.optics.Optic
    options:
        show_root_heading: true

### ::: starplot.optics.Binoculars
    options:
        merge_init_into_class: true
        show_root_heading: true
        show_docstring_attributes: true

### ::: starplot.optics.Scope
    options:
        merge_init_into_class: true
        show_root_heading: true
        show_docstring_attributes: true

### ::: starplot.optics.Refractor
    options:
        merge_init_into_class: true
        show_root_heading: true
        show_docstring_attributes: true

### ::: starplot.optics.Reflector
    options:
        merge_init_into_class: true
        show_root_heading: true
        show_docstring_attributes: true

### ::: starplot.optics.Camera
    options:
        merge_init_into_class: true
        show_root_heading: true
        show_docstring_attributes: true
