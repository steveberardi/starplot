from datetime import datetime
from zoneinfo import ZoneInfo

from starplot import OpticPlot, DSO, Observer, _
from starplot.callables import color_by_bv
from starplot.models import Refractor
from starplot.styles import PlotStyle, extensions

dt = datetime(2023, 12, 16, 21, 0, 0, tzinfo=ZoneInfo("US/Pacific"))

observer = Observer(
    dt=dt,
    lat=32.97,
    lon=-117.038611,
)

style = PlotStyle().extend(
    extensions.BLUE_GOLD,
    extensions.OPTIC,
)

m42 = DSO.get(m="42")
p = OpticPlot(
    # Orion Nebula
    ra=m42.ra,
    dec=m42.dec,
    observer=observer,
    # TV-85
    optic=Refractor(
        focal_length=600,
        eyepiece_focal_length=11,
        eyepiece_fov=100,
    ),
    style=style,
    resolution=2600,
    autoscale=True,
)
p.stars(where=[_.magnitude < 14], color_fn=color_by_bv, bayer_labels=True)
p.dsos(where=[_.magnitude < 4.1], where_labels=[False])
p.info()
p.export("optic_orion_nebula.png", padding=0.1, transparent=True)
