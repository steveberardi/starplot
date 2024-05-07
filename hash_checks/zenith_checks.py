from pathlib import Path
from datetime import datetime

from pytz import timezone

from starplot import styles
from starplot.map import MapPlot, Projection

HERE = Path(__file__).resolve().parent
DATA_PATH = HERE / "data"

STYLE = styles.PlotStyle().extend(
    styles.extensions.BLUE_MEDIUM,
)

JUNE_2023 = datetime.now(timezone("US/Pacific")).replace(2023, 6, 20, 21, 0, 0, 0)

RESOLUTION = 2400


def _zenith():
    p = MapPlot(
        projection=Projection.ZENITH,
        lat=32.97,
        lon=-117.038611,
        dt=JUNE_2023,
        style=STYLE,
        resolution=RESOLUTION,
    )
    p.stars(mag=4.6, style__marker__size=25)
    p.constellations()
    p.ecliptic(style__line__width=8)
    p.celestial_equator(style__line__width=8)
    p.legend(style__location=styles.LegendLocationEnum.OUTSIDE_BOTTOM)
    return p


zenith_base = _zenith()


def check_zenith_base():
    filename = DATA_PATH / "zenith-base.png"
    zenith_base.export(filename)
    return filename
