# <img src="docs/banner.svg" width="900">
![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/steveberardi/starplot/test.yml?style=for-the-badge)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/starplot?style=for-the-badge)
![PyPI](https://img.shields.io/pypi/v/starplot?style=for-the-badge)

**starplot** is a Python library for creating star charts and maps.

- ⭐ **Zenith Plots** - showing the stars from a specific time/location
- 🗺️ **Map Plots** - including North/South polar and Mercator projections
- 🎨 **Custom Styles** - for all objects
- 📥 **Export** - png, svg
- 🧭 **Label Collision Avoidance** - via `adjustText`

## Examples
*Zenith plot of the stars from a specific time/location:*
![starchart-blue](examples/starchart-blue.png)

*Map around the constellation Orion, with M42 marked:*
![map-orion](examples/mercator-orion.png)

[More examples](examples/)

## Getting Started

To create a star chart for tonight's sky as seen from [Palomar Mountain](https://en.wikipedia.org/wiki/Palomar_Mountain) in California:

```python
from datetime import datetime
from pytz import timezone
import starplot as sp

p = sp.ZenithPlot(
    lat=33.363484, 
    lon=-116.836394,
    dt=timezone("America/Los_Angeles").localize(datetime.now().replace(hour=22)),
    limiting_magnitude=4.6,
    style=sp.styles.BLUE,
    resolution=2000,
)
p.export("starchart.png")
```

## Core Dependencies

- matplotlib
- pandas
- numpy
- skyfield
- geopandas
- cartopy
- pydantic
- adjustText

## Coming Soon

- Documentation

## License
[MIT License](LICENSE)
