# <img src="https://raw.githubusercontent.com/steveberardi/starplot/plot-framework/docs/banner.png" width="600">
![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/steveberardi/starplot/test.yml?style=for-the-badge)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/starplot?style=for-the-badge)
![PyPI](https://img.shields.io/pypi/v/starplot?style=for-the-badge)

**starplot** is a Python library for creating star charts and maps.

## Example
![Example](https://raw.githubusercontent.com/steveberardi/starplot/main/examples/starchart-blue.png)

For more styles, check out the [examples](examples/).

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
p.export("starchart.svg", format="svg")
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
