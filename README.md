# <img src="https://raw.githubusercontent.com/steveberardi/starplot/main/docs/images/favicon.svg" width="48" style="vertical-align:middle"> Starplot
![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/steveberardi/starplot/test.yml?style=for-the-badge&color=a2c185)
![Python](https://img.shields.io/pypi/pyversions/starplot?style=for-the-badge&color=85A2C1)
![PyPI](https://img.shields.io/pypi/v/starplot?style=for-the-badge&color=85C0C1)
![License](https://img.shields.io/github/license/steveberardi/starplot?style=for-the-badge&color=A485C1)

**Starplot** is a Python library for creating star charts and maps.

- ⭐ **Zenith Plots** - showing the stars from a specific time/location
- 🗺️ **Map Plots** - including North/South polar and Mercator projections
- 🔭 **Optic Plots** - simulates what you'll see through an optic (e.g. binoculars, telescope) from a time/location
- 🪐 **Planets and Deep Sky Objects (DSOs)**
- 🎨 **Custom Styles** - for all objects
- 📥 **Export** - png, svg
- 🧭 **Label Collision Avoidance**

## Examples
*Zenith plot of the stars from a specific time/location:*
![starchart-blue](https://starplot.dev/images/examples/star_chart_basic.png)

*Map around the constellation Orion:*
![map-orion](https://starplot.dev/images/examples/map_orion.png)

*Optic plot of The Pleiades through a refractor as seen from a specific time/location:*
![optic-pleiades](https://starplot.dev/images/examples/optic_m45.png)

## Basic Usage

To create a star chart for tonight's sky as seen from [Palomar Mountain](https://en.wikipedia.org/wiki/Palomar_Mountain) in California:

```python
from datetime import datetime
from pytz import timezone
import starplot as sp

tz = timezone("America/Los_Angeles")

p = sp.MapPlot(
    projection=sp.Projection.ZENITH,
    lat=33.363484,
    lon=-116.836394,
    dt=datetime.now(tz).replace(hour=22),
    style=sp.styles.PlotStyle().extend(
        sp.styles.extensions.BLUE_MEDIUM,
        sp.styles.extensions.ZENITH,
    ),
    resolution=2000,
)
p.constellations()
p.stars(mag=4.6)
p.export("starchart.png")
```

## Documentation

[https://starplot.dev](https://starplot.dev)


## Demo
For a demo of Starplot's zenith plots, check out: 

[Sky Atlas - Star Chart Creator](https://skyatlas.app/star-charts/)

## Discord

Chat with other starplotters on our Discord server:

https://discord.gg/bwazdyD7

## Core Dependencies

- matplotlib
- pandas
- numpy
- geopandas
- cartopy
- skyfield
- pydantic
- adjustText

## Coming Soon
- 🌑 Planet moons
- ✴️ Custom markers
- 🚀 Plotting Optimizations
- 📐 More Nebula outline levels
- ⚖️ Better auto font-size adjustment

See more details on the [Public Roadmap](https://starplot.notion.site/aaa0dd71c17943f89850c9a8c43ade50)

## License
[MIT License](https://github.com/steveberardi/starplot/blob/main/LICENSE)
