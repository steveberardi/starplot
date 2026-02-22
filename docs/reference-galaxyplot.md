**Galaxy plots will plot everything in galactic coordinates, using a Mollweide projection**. These plots will always plot the entire galactic sphere, since that's how they're most commonly used.

Although they plot everything in galactic coordinates, all functions still expect equatorial coordinates (RA/DEC). This decision was made for two reasons: it seems most astronomical data is presented in equatorial coordinates, and creating a transformation framework in Starplot would be a pretty large project so it'll be reserved for a future version.

Stars on galaxy plots are plotted in their [_astrometric_ positions](reference-positions.md).

!!! tip "New Feature - Feedback wanted!"

    These plots are a newer feature of Starplot (introduced in version 0.20.0), and will continue to evolve in future versions. 
    
    If you notice any unexpected behavior or you think there's a useful feature missing, please [open an issue on GitHub](https://github.com/steveberardi/starplot/issues).
    

::: starplot.GalaxyPlot
    options:
        inherited_members: true
        merge_init_into_class: true
        show_root_heading: true
        docstring_section_style: list

