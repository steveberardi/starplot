import time

from datetime import datetime
from zoneinfo import ZoneInfo

from shapely import Polygon

from starplot.data.catalogs import BIG_SKY
from starplot import (
    Star,
    DSO,
    Observer,
    Constellation,
    Miller,
    Mollweide,
    StereoNorth,
    _,
)
from starplot.styles import (
    PlotStyle,
    extensions,
    MarkerStyle,
    PathStyle,
    LineStyle,
    PolygonStyle,
    LabelStyle,
)
from starplot.svg import MapPlot


start = time.perf_counter()

dt = datetime(2023, 12, 16, 21, 0, 0, tzinfo=ZoneInfo("US/Pacific"))

style = PlotStyle().extend(
    # extensions.BLUE_NIGHT,
    extensions.BLUE_MEDIUM,
    # extensions.GRADIENT_TRUE_NIGHT,
    extensions.MAP,
    {
        "arrow": {"body_width": 10, "head_width": 30, "head_height": 40},
        "figure_padding": 60,
    },
)

observer = Observer(
    dt=dt,
    lat=33.363484,
    lon=-116.836394,
)

style.constellation_lines.width = 2
style.constellation_borders.width = 1
style.dso_open_cluster.marker.edge_width = 1.6

CENTER_RA = 180

cas = Constellation.get(iau_id="cas")

c = MapPlot(
    ra_min=18 * 15,
    ra_max=26 * 15,
    dec_min=10,
    dec_max=60,
    # projection=Miller(center_ra=CENTER_RA),
    projection=StereoNorth(center_ra=19 * 15),
    # projection=Mollweide(),
    style=style,
    resolution=4000,
    scale=0.98,
    debug=True,
    # debug_text=True,
    # clip_path=Polygon(cas.border.coords),
)


c.constellations()
c.constellation_borders()

c.stars(
    where=[_.magnitude < 6],
    # catalog=BIG_SKY,
    bayer_labels=True,
    flamsteed_labels=True,
)

c.constellation_labels()


c.ecliptic()
c.celestial_equator()
c.milky_way()

c.gridlines()


m57 = DSO.get(m="57")

c.arrow(target=(m57.ra, m57.dec))


# c.point_label_handler.plot_on_fail = True
# c.point_label_handler.attempts = 1

c.open_clusters(where_true_size=[False])

c.globular_clusters(where_true_size=[False])

c.rectangle(
    center=(m57.ra, m57.dec),
    height_degrees=6,
    width_degrees=8,
    style__edge_color="red",
)

c.title("Hello World!!", style__border_color="black", style__border_width=400)

# c.circle(
#     center=(m57.ra, m57.dec + 15),
#     radius_degrees=6,
#     style__edge_color="yellow",
# )

# c.tissot()


# print(
#     c.canvas.tx.transform_bounds(*c.canvas.projected_bounds, direction='INVERSE')
# )


c.export("temp/orion.svg")
c.export("temp/orion.png")


elapsed = time.perf_counter() - start
print(f"{elapsed:.5f}s")
