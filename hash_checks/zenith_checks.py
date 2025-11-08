from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

from starplot import ZenithPlot, Observer, styles, override_settings, _

HERE = Path(__file__).resolve().parent
DATA_PATH = HERE / "data"

STYLE = styles.PlotStyle().extend(
    styles.extensions.BLUE_MEDIUM,
)

JUNE_2023 = datetime(2023, 6, 20, 21, 0, 0, 0, tzinfo=ZoneInfo("US/Pacific"))

RESOLUTION = 3800


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
    p.legend(style__location=styles.LegendLocationEnum.INSIDE_BOTTOM_RIGHT)
    p.constellation_labels()
    return p


zenith_base = _zenith()


def check_zenith_base():
    filename = DATA_PATH / "zenith-base.png"
    zenith_base.export(filename)
    return filename


def check_zenith_gradient():
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
    p.constellation_labels()
    filename = DATA_PATH / "zenith-gradient.png"
    p.export(filename)
    return filename


@override_settings(language="zh-cn")
def check_zenith_chinese():
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
                        "font_name": "Noto Sans SC",
                    }
                },
                "horizon": {
                    "label": {
                        "font_name": "Noto Sans SC",
                    }
                },
                "constellation_labels": {
                    "font_name": "Noto Sans SC",
                },
            },
        ),
        resolution=RESOLUTION,
        autoscale=True,
    )
    p.horizon()
    p.constellations()
    p.stars(where=[_.magnitude < 4.6], where_labels=[_.magnitude < 4])
    p.constellation_labels()
    filename = DATA_PATH / "zenith-chinese.png"
    p.export(filename)
    return filename
