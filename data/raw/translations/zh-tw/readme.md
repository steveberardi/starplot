This directory contains the raw data that will be used in translating text in Starplot to chinese languages(zh-TW).
<img width="2005" height="2004" alt="starchart_test_TW" src="https://github.com/user-attachments/assets/7b05e465-f67c-41b4-a07b-bdeedeed2efc" />
## Basic Usage

To create a star chart for tonight's sky in Asia/Taipei:

```python
# -*- coding: utf-8 -*-
'''
import matplotlib as mpl
mpl.rcParams['font.family'] = ['serif']
mpl.rcParams['font.serif'] = ['Noto Sans TC']
'''
from datetime import datetime
from zoneinfo import ZoneInfo

from starplot import ZenithPlot, settings, Observer, _
from starplot.styles import PlotStyle, LabelStyle, LegendStyle, extensions

#from starplot.styles import fonts
#fonts.load()

tz = ZoneInfo("Asia/Taipei")
print("現在時間 : ",datetime.now(tz))
#dt = datetime.now(tz)
# Observering time
dt = datetime.now(tz).replace(day=15,hour=20,minute=00)
dt_format = dt.strftime("%Y/%m/%d %H:%M")  
print("觀測時間 : ",dt_format)
dt_print = dt.strftime("%Y-%m-%d %H:%M") 

observer = Observer(
    dt=dt,
    #lat=33.363484,
    #lon=-116.836394,
    lat=25.04776,
    lon=121.53185,
)

# Local Language Setting 
#settings.language =  "en-us"
#settings.language =  "fr"
settings.language = "zh-TW"

style=PlotStyle().extend(
        extensions.BLUE_GOLD,
        extensions.GRADIENT_PRE_DAWN,
    )

p = ZenithPlot(
    observer=observer,
    style=style,
    resolution=3600,
    autoscale=True,
)
#-------- Style Label Font Name Setting --------------
style.legend = LegendStyle()
style.legend.font_name= 'Noto Sans TC'
style.legend.title_font_name = 'Noto Sans TC'

style.constellation_labels.font_name = 'Noto Sans TC'
style.ecliptic.label.font_name = 'Noto Sans TC'
style.celestial_equator.label.font_name = 'Noto Sans TC'
style.horizon.label.font_name = 'Noto Sans TC'
style.star.label.font_name = 'Noto Sans TC'
style.moon.label.font_name = 'Noto Sans TC'
style.planets.label.font_name= 'Noto Sans TC'
#------------------------------------------------------

p.stars(where=[_.magnitude < 4.6], where_labels=[_.magnitude < 2.1])
p.galaxies(where=[_.magnitude < 6], true_size=False, where_labels=[False])
p.open_clusters(where=[_.magnitude < 6], true_size=False, where_labels=[False])

p.moon()
p.planets()
p.horizon()
p.constellations()
p.constellation_labels()
p.ecliptic()
p.celestial_equator()
p.milky_way()

p.legend("台北市  "+ dt_print)
#p.legend("Asia/Taipei  "+ dt_print)

'''
p.marker(
    ra=12.36 * 15,
    dec=25.85,
    style={
        "marker": {
            "size": 60,
            "symbol": "circle",
            "fill": "none",
            "color": None,
            "edge_color": "hsl(44, 70%, 73%)",
            "edge_width": 2,
            "line_style": [1, [2, 3]],
            "alpha": 1,
            "zorder": 100,
        },
        "label": {
            "zorder": 200,
            "font_size": 22,
            "font_weight": "bold",
            "font_color": "hsl(44, 70%, 64%)",
            "font_alpha": 1,
            "offset_x": "auto",
            "offset_y": "auto",
            "anchor_point": "top right",
        },
    },
    label="Mel 111",
)
'''
p.export("Starchart_TW.png", transparent=True, padding=0.1)
```
