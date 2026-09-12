from datetime import datetime
from zoneinfo import ZoneInfo

from utils import actual_filename

from starplot import (
    CollisionHandler,
    Observer,
    ZenithPlot,
    _,
    override_settings,
    styles,
)

STYLE = styles.PlotStyle().extend(
    styles.extensions.BLUE_MEDIUM,
)

JUNE_2023 = datetime(2023, 6, 20, 21, 0, 0, 0, tzinfo=ZoneInfo("US/Pacific"))

RESOLUTION = 4096

HANDLER = CollisionHandler(seed=1, allow_constellation_line_collisions=True)


def _zenith():
    observer = Observer(
        lat=32.97,
        lon=-117.038611,
        dt=JUNE_2023,
    )
    p = ZenithPlot(
        observer=observer,
        style=STYLE,
        resolution=RESOLUTION,
        autoscale=True,
    )
    p.horizon()
    p.constellations()
    p.stars(where=[_.magnitude < 4.6], where_labels=[_.magnitude < 3])
    p.ecliptic(style__line__width=8)
    p.celestial_equator(style__line__width=8)
    p.legend(style__location=styles.LegendLocation.INSIDE_BOTTOM_RIGHT)
    p.constellation_labels(collision_handler=HANDLER)
    return p


zenith_base = _zenith()


def e2e_zenith_base():
    filename = actual_filename("zenith_base")
    zenith_base.export(filename)
    return filename


def e2e_zenith_gradient():
    p = ZenithPlot(
        observer=Observer(
            lat=32.97,
            lon=-117.038611,
            dt=JUNE_2023,
        ),
        style=styles.PlotStyle().extend(
            styles.extensions.BLUE_GOLD,
            styles.extensions.GRADIENT_PRE_DAWN,
        ),
        resolution=RESOLUTION,
        autoscale=True,
    )
    p.horizon()
    p.constellations()
    p.stars(where=[_.magnitude < 4.6], where_labels=[_.magnitude < 3])
    p.ecliptic(style__line__width=8)
    p.celestial_equator(style__line__width=8)
    p.constellation_labels(collision_handler=HANDLER)
    filename = actual_filename("zenith_gradient")
    p.export(filename)
    return filename


@override_settings(language="zh-cn")
def e2e_zenith_chinese():
    p = ZenithPlot(
        observer=Observer(
            lat=32.97,
            lon=-117.038611,
            dt=JUNE_2023,
        ),
        style=styles.PlotStyle().extend(
            styles.extensions.BLUE_GOLD,
            styles.extensions.GRADIENT_PRE_DAWN,
            {
                "star": {
                    "label": {
                        "font_name": "Noto Sans CJK SC",
                    }
                },
                "horizon": {
                    "label": {
                        "font_name": "Noto Sans CJK SC",
                    }
                },
                "constellation_labels": {
                    "font_name": "Noto Sans CJK SC",
                },
            },
        ),
        resolution=RESOLUTION,
        autoscale=True,
    )
    p.horizon()
    p.constellations()
    p.stars(where=[_.magnitude < 4.6], where_labels=[_.magnitude < 4])
    p.constellation_labels(collision_handler=HANDLER)
    filename = actual_filename("zenith_chinese")
    p.export(filename)
    return filename
