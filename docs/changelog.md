
## v0.10.x
- Adds function for plotting text
- Adds `where` kwarg to star/DSO plotting functions to selectively plot stars
- Adds easier way to override style properties on plotting functions - thanks to Graham Schmidt
- Adds function to plot the Sun - thanks to Graham Schmidt
- Adds option to illustrate the Moon's phase - thanks to Graham Schmidt
- Adds `objects` property to plots that stores lists of objects that have been plotted
- Adds object finder helpers
- Adds customizable anchor points for text labels
- Adds Pluto as a planet :)
- Fixes clipping issues with polygons

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
