from datetime import datetime
from zoneinfo import ZoneInfo

from starplot import (
    HorizonPlot,
    PlotStyle,
    style_extensions,
    DSO,
    Constellation,
    Observer,
    _,
    Binoculars,
)

style = PlotStyle().extend(
    style_extensions.BLUE_NIGHT,
    style_extensions.MAP,
    style_extensions.GRADIENT_ASTRONOMICAL_TWILIGHT,
)

tz = ZoneInfo("US/Pacific")
dt = datetime(2024, 11, 2, 21, 0, 0, 0, tzinfo=tz)

observer = Observer(
    dt=dt,
    lat=33.363484,
    lon=-116.836394,
)

cas = Constellation.get(iau_id="cas")
umi = Constellation.get(iau_id="umi")
per = Constellation.get(iau_id="per")

p = HorizonPlot(
    altitude=(0, 70),
    azimuth=(325, 440),
    observer=observer,
    style=style,
    resolution=4096,
    scale=1.25,
)
p.constellations(where=[_.iau_id.isin(["cas", "umi", "per"])])
p.stars(
    where=[_.hip.isin(cas.star_hip_ids + umi.star_hip_ids + per.star_hip_ids)],
    where_labels=[_.magnitude < 2],
)
p.style.dso_open_cluster.label.font_size = 27
p.open_clusters(
    where=[_.name.isin(["NGC0884", "NGC0869"])],
    true_size=False,
)
double_cluster = DSO.get(name="NGC0884")
p.optic_fov(
    ra=double_cluster.ra,
    dec=double_cluster.dec,
    optic=Binoculars(
        fov=65,
        magnification=10,
    ),
)
p.constellation_labels()
p.horizon()
p.style.gridlines.line.width = 2
p.gridlines()

p.export("horizon_double_cluster.png", padding=0.25)
