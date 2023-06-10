# ⭐ starplot 💫
Python library for creating star charts and maps

## Examples
![Example](examples/starchart-blue.png)

### More Styles
<img src="examples/starchart-chalk.png" height="300" width="300">
<img src="examples/starchart-red.png" height="300" width="300">
<img src="examples/starchart-mono.png" height="300" width="300">

## Getting Started

To create a star chart for today as seen from [Palomar Mountain](https://en.wikipedia.org/wiki/Palomar_Mountain) in California:
```python
from datetime import datetime
from starplot.charts import create_star_chart
from starplot.styles import BLUE

create_star_chart(
    lat=33.363484, 
    lon=-116.836394
    dt=datetime.now(),
    tz_identifier="America/Los_Angeles", 
    filename="starchart.png",
    style=BLUE,
)
```

## Coming Soon

- Deep Sky Objects (DSOs)
- Support for plotting additional objects (and styling per object)
- Documentation

## How To
- Create basic star chart
- Create new style
- Add additional objects

