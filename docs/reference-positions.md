
Starplot can plot objects in two types of positions: astrometric and apparent.


### Astrometric Position

Astrometric position is the "true" geometric position of an object in space, corrected for the time it takes for light to travel. For example, from Earth we see Jupiter where it was more than 30 minutes ago.

This is typically the position you'd want to plot when creating reference materials that are not tied to a specific time and place of observation. For example: printed sky atlases, constellation charts, etc.

Plots that use astrometric positions:

- [MapPlot](reference-mapplot.md)
- [ZenithPlot](reference-zenithplot.md)


### Apparent Position
Apparent position is where the object _appears_ to be in the sky as seen by the observer, which is affected by these observational effects:

- Light-time delay
- Aberration of light
- Atmospheric refraction (bends light as it passes through Earth's atmosphere)
- Precession and nutation (wobbles in Earth's rotation axis)

This is typically the position you'd want to plot when you're creating charts for observation at a specific time and place. For example: what the Pleiades looks like through a refractor telescope at a certain time/place.

Plots that use apparent positions:

- [OpticPlot](reference-opticplot.md)
- [HorizonPlot](reference-horizonplot.md)

<br/><br/><br/>
