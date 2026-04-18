import time

from datetime import datetime
from zoneinfo import ZoneInfo
from pprint import pprint

from shapely import Polygon

from starplot.data.catalogs import BIG_SKY
from starplot import (
    MapPlot,
    Star,
    DSO,
    Observer,
    Constellation,
    Miller,
    Mollweide,
    StereoNorth,
    Equidistant,
    Orthographic,
    Stereographic,
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

from starplot.config import settings as StarplotSettings

StarplotSettings.svg_text_type = "element"

start = time.perf_counter()

dt = datetime(2023, 12, 16, 21, 0, 0, tzinfo=ZoneInfo("US/Pacific"))

style = PlotStyle().extend(
    # extensions.BLUE_NIGHT,
    extensions.BLUE_MEDIUM,
    # extensions.GRADIENT_ASTRONOMICAL_TWILIGHT,
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
style.background_gradient_direction = "linear"

CENTER_RA = 180

cas = Constellation.get(iau_id="cas")

c = MapPlot(
    ra_min=0 * 15,
    ra_max=24 * 15,
    dec_min=-30,
    dec_max=90,
    # projection=Miller(center_ra=23/2 * 15),
    # projection=Equidistant(center_ra=12 * 15, center_dec=35),
    # projection=Mollweide(),
    # projection=Equidistant(center_ra=observer.lst, center_dec=45),
    # projection=Stereographic(center_ra=12*15, center_dec=45),
    projection=StereoNorth(),
    style=style,
    resolution=3000,
    scale=0.6,
    debug=True,
    # debug_text=True,
    clip_path=Polygon(cas.border.coords),
)


c.constellations()
c.constellation_borders()

c.stars(
    where=[_.magnitude < 6],
    where_labels=[_.magnitude < 4],
    # catalog=BIG_SKY,
    bayer_labels=True,
    flamsteed_labels=True,
)

c.constellation_labels()
c.ecliptic()
c.celestial_equator()
c.milky_way()

# print(c._extent_mask().bounds)

c.gridlines()


# m57 = DSO.get(m="57")

# m31 = DSO.get(m="31")

# # c.arrow(target=(m57.ra, m57.dec))


# # c.point_label_handler.plot_on_fail = True
# # c.point_label_handler.attempts = 1

c.open_clusters(where_true_size=[False])

c.globular_clusters(where_true_size=[False])
c.galaxies(where=[_.magnitude < 9], where_true_size=[False])
c.nebula(where_true_size=[_.size > 0.01])


# c.rectangle(
#     center=(m57.ra, m57.dec),
#     height_degrees=6,
#     width_degrees=8,
#     style__edge_color="red",
# )

# c.title(
#     "Hello World!!",
#     # style__border_color="black",
#     # style__border_width=400,
# )

# c.marker(
#     ra=m31.ra,
#     dec=m31.dec,
#     style__marker__fill="full",
#     style__marker__color="hsl(195deg 100% 24%)",
#     style__marker__edge_color="hsl(195deg 100% 64%)",
#     style__marker__edge_width=2,
#     style__marker__symbol="comet",
#     style__marker__size=50,
# )

# c.legend(
#     style__location="outside top right",
#     style__margin_y=0,
# )

# c.legend(
#     style__location="outside bottom right",
#     style__margin_y=0,
#     magnitude_scale=True,
# )
c.legend(
    style__location="outside top right",
    style__margin_y=0,
    style__margin_x=40,
    magnitude_scale=True,
)



c.export("temp/orion.svg")
# c.export("temp/orion.png")


elapsed = time.perf_counter() - start
print(f"{elapsed:.5f}s")
