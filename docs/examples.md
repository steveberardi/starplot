
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
