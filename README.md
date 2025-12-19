# <img src="https://raw.githubusercontent.com/steveberardi/starplot/main/docs/images/logo.svg" width="48" style="vertical-align:middle"> Starplot
![Python](https://img.shields.io/pypi/pyversions/starplot?style=for-the-badge&color=6388b0)
![PyPI](https://img.shields.io/pypi/v/starplot?style=for-the-badge&color=57a8a8)
![License](https://img.shields.io/github/license/steveberardi/starplot?style=for-the-badge&color=8b63b0)
![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/steveberardi/starplot/test.yml?style=for-the-badge&color=88b063)

**Starplot** is a Python library for creating star charts and maps of the sky.

- 🗺️ **Maps** - including 10+ customizable projections
- ⭐ **Zenith Charts** - shows the entire sky at a specific time and place
- 🌃 **Horizon Charts** - shows the horizon at a specific time and place
- 🔭 **Optic Simulations** - shows what you'll see through an optic (e.g. telescope) at a specific time and place
- 🪐 **Planets and Deep Sky Objects (DSOs)** - more than 14,000 objects built-in
- ☄️ **Comets and Satellites** - easy trajectory plotting
- 🎨 **Custom Styles** - for all objects and with 8+ built-in themes
- 📥 **Export** - png, svg, jpeg
- 🚀 **Data Backend** - powered by DuckDB + Ibis for fast object lookup
- 🧭 **Label Collision Avoidance** - ensuring all labels are readable
- 🌐 **Localization** - label translations for French, Chinese, and Persian (coming soon!)

## Examples
*Zenith chart of the stars from a specific time/location:*
![starchart-blue](https://starplot.dev/images/examples/star_chart_basic.png)

*Map around the constellation Orion:*
![map-orion](https://starplot.dev/images/examples/map_orion.png)

*The Pleiades star cluster, as seen through a refractor telescope from a specific time and location:*
![optic-pleiades](https://starplot.dev/images/examples/optic_m45.png)

## Basic Usage

To create a star chart for tonight's sky as seen from [Palomar Mountain](https://en.wikipedia.org/wiki/Palomar_Mountain) in California:

```python
from datetime import datetime
from zoneinfo import ZoneInfo

from starplot import ZenithPlot, Observer, styles, _

tz = ZoneInfo("America/Los_Angeles")
dt = datetime.now(tz).replace(hour=22)

observer = Observer(
    dt=dt,
    lat=33.363484,
    lon=-116.836394,
)

p = ZenithPlot(
    observer=observer,
    style=styles.PlotStyle().extend(
        styles.extensions.BLUE_MEDIUM,
    ),
    resolution=4096,
    autoscale=True,
)
p.constellations()
p.stars(where=[_.magnitude < 4.6])
p.constellation_labels()
p.horizon()
p.export("starchart.png")
```

## Documentation

[https://starplot.dev](https://starplot.dev)


## Demo
For a demo of Starplot's zenith charts, check out: 

[Sky Atlas - Star Chart Creator](https://skyatlas.app/star-charts/)

## Getting Help / Updates

- Chat with other starplotters on our [Discord server](https://discord.gg/WewJJjshFu)
- [Follow us on Bluesky](https://bsky.app/profile/starplot.dev)
- [Join our newsletter](https://buttondown.com/starplot)
- [See more examples at Starplotting.com](https://starplotting.com/)

## Contributing

Contributing to Starplot is welcome and very much appreciated! Please see [here](CONTRIBUTING.md) for details.

## Coming Soon
- 📡 Custom data catalogs
- 🧮 Coordinate system helpers
- 🌑 Planet moons
- ✴️ Custom markers
- 😄 🔭 Clear skies

See more details on the [Public Roadmap](https://trello.com/b/sUksygn4/starplot-roadmap)

## License
[MIT License](https://github.com/steveberardi/starplot/blob/main/LICENSE)
