# ![starplot](https://raw.githubusercontent.com/steveberardi/starplot/plot-framework/docs/logo.png) starplot ⭐
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
from starplot.charts import create_star_chart
from starplot.styles import BLUE

create_star_chart(
    lat=33.363484, 
    lon=-116.836394,
    dt=datetime.now().replace(hour=22),
    tz_identifier="America/Los_Angeles", 
    filename="starchart.png",
    style=BLUE,
)
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
MIT License

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

