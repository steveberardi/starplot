## v0.12.x

- Adds Shapely geometry to all sky object models, including support for `intersects` in `where` clauses
- Adds kwarg to map plots to allow custom clip paths
- Adds callables for star/dso labels
- Adds a `line` function for plotting lines
- Adds the standard marker for globular clusters (circle with a cross) and double stars
- Adds an ellipse marker for galaxies
- Adds colors for some DSO labels that were missing them in some style extensions
- Removed the kwarg `types` from `dsos`, so ALL DSO types are plotted by default
- [**v0.12.1**] Fixes issue with plotting the Milky Way when it consists of multiple polygons

## v0.11.x
[Documentation](https://archives.starplot.dev/0.11.4/)

- Replaces Tycho-1 stars with an abridged version of the [Big Sky Catalog](https://github.com/steveberardi/bigsky)
- Adds style option for a star's edge color (previously this was forced to be the background color)
- Adds cardinal direction labels to the horizon plotting function
- Removes behavior that automatically plots the cardinal direction border on zenith plots
- Adds function for plotting the zenith
- Adds support for downloading the full [Big Sky Catalog](https://github.com/steveberardi/bigsky) (2.5+ million stars)
- Various (minor) plotting optimizations
- Increases star sizes on map plots
- Adds TYC id to stars (if available)
- Adds the following projections: Robinson, Lambert Azimuthal Equal-Area
- Adds a constellation model, allowing you to selectively plot objects by their constellation
- [**v0.11.1**] Fixes default horizon style to be consistent with grayscale extension
- [**v0.11.2**] Adds `requests` as a required dependency
- [**v0.11.3**] Fixes bug with plotting the celestial equator
- [**v0.11.4**] Fixes bug with filtering DSOs by NGC/IC identifier

## v0.10.x
[Documentation](https://archives.starplot.dev/0.10.2/)

- Adds function for plotting text
- Adds `where` kwarg to star/DSO plotting functions to selectively plot stars
- Adds easier way to override style properties on plotting functions - thanks to Graham Schmidt
- Adds function to plot the Sun - thanks to Graham Schmidt
- Adds option to illustrate the Moon's phase - thanks to Graham Schmidt
- Adds `objects` property to plots, which stores lists of objects that have been plotted
- Adds object finder helpers
- Adds customizable anchor points for text labels
- Adds Pluto as a planet :)
- Fixes clipping issues with polygons
- Fixes a few issues with gridlines
- [**v0.10.1**]
    - Fixes bug with plotting planets as true apparent size
    - Adds lat/lon kwargs to Sun/Moon/Planet models to allow _apparent_ RA/DEC calculation
- [**v0.10.2**] Fixes a few issues with plotting legends

## v0.9.x
[Documentation](https://archives.starplot.dev/0.9.1/)

- Added perspective projections (Orthographic, Stereographic) to map plots - many thanks to @bathoorn
- Zenith plots are now a type of projection for map plots, to support plotting the Milky Way, constellation borders and more - many thanks to @bathoorn
- Removed the visible style property and instead now you control what is plotted by calling functions on the plot (e.g. p.stars(mag=8)) to be more consistent with other plotting frameworks and allow more control over what's plotted and how. For example, now you can do things like plotting very bright stars with a different marker (and sizes, etc) than dimmer stars.
- Optional callables for calculating star size/alpha/color when plotting stars
- Nebula outlines! via OpenNGC
- Stars are now plotted in order of their calculated size, which prevents "bigger" stars from hiding "smaller" stars
- Added more marker symbols and style extensions
- [**v0.9.1**] Fixes bug with plotting moon and planets as their true size

## v0.8.x
[Documentation](https://archives.starplot.dev/0.8.4/)

- Adds new Milky Way outline created from a NASA image, and broken into sections to speed up plotting/exporting
- Adds styling support for more DSO types
- Adds support for Mollweide projection
- Fixes map and optic plots to handle wrapping of RA (e.g. plotting RA extent from 2h -> 18h)
- Fixes a bug in all plots that prevented some star styles to not get applied
- [**v0.8.1**] Fixes a small bug in adjusting RA extent on map plots
- [**v0.8.2**] Fixes a small bug in determining if a RA/DEC is in bounds of a plot
- [**v0.8.3**] More consistent polygon/circle sizing across projections
- [**v0.8.4**] Fixes a small bug in plotting text labels of DSOs, which prevented some styles from getting applied

<br/><br/>
