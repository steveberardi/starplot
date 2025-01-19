from datetime import datetime

from pytz import timezone

from starplot import HorizonPlot, PlotStyle, style_extensions, DSO, Constellation, _


style = PlotStyle().extend(
    style_extensions.BLUE_GOLD,
    style_extensions.MAP,
)

tz = timezone("US/Pacific")
dt = tz.localize(datetime(2024, 11, 2, 21, 0, 0, 0))

cas = Constellation.get(iau_id="cas")
umi = Constellation.get(iau_id="umi")
per = Constellation.get(iau_id="per")

p = HorizonPlot(
    altitude=(0, 70),
    azimuth=(320, 435),
    lat=33.363484,
    lon=-116.836394,
    dt=dt,
    style=style,
    resolution=4096,
    scale=1,
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
    label_fn=lambda d: f"{d.ngc}",
)
double_cluster = DSO.get(name="NGC0884")
p.bino_fov(
    ra=double_cluster.ra,
    dec=double_cluster.dec,
    fov=65,
    magnification=10,
)
p.constellation_labels()
p.horizon(show_degree_labels=False, show_ticks=False)
p.gridlines()

p.export("horizon_double_cluster.png")
