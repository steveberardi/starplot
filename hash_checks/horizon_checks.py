from pathlib import Path
from datetime import datetime

from pytz import timezone

from starplot import styles, HorizonPlot, _

HERE = Path(__file__).resolve().parent
DATA_PATH = HERE / "data"

STYLE = styles.PlotStyle().extend(
    styles.extensions.BLUE_MEDIUM,
    styles.extensions.MAP,
)

RESOLUTION = 4096

AUTO_ADJUST_SETTINGS = {"seed": 1}


def _horizon():
    dt = timezone("US/Pacific").localize(datetime(2024, 8, 30, 21, 0, 0, 0))

    p = HorizonPlot(
        altitude=(0, 50),
        azimuth=(150, 210),
        lat=36.606111,  # Lone Pine, California
        lon=-118.079444,
        dt=dt,
        style=STYLE,
        resolution=RESOLUTION,
        scale=1,
    )
    p.constellations()
    p.constellation_borders()
    p.milky_way()
    p.stars(where=[_.magnitude < 5])
    p.ecliptic()
    p.horizon()
    p.constellation_labels(auto_adjust_settings=AUTO_ADJUST_SETTINGS)
    p.gridlines()
    return p


def check_horizon_base():
    horizon_base = _horizon()
    filename = DATA_PATH / "horizon-base.png"
    horizon_base.export(filename)
    return filename


def check_horizon_north_celestial_pole():
    dt = timezone("US/Pacific").localize(datetime(2024, 8, 30, 21, 0, 0, 0))

    p = HorizonPlot(
        altitude=(0, 50),
        azimuth=(330, 390),
        lat=36.606111,  # Lone Pine, California
        lon=-118.079444,
        dt=dt,
        style=STYLE,
        resolution=RESOLUTION,
        scale=1,
    )
    p.constellations()
    p.constellation_borders()
    p.milky_way()
    p.stars(where=[_.magnitude < 5])
    p.ecliptic()
    p.horizon()
    p.constellation_labels(auto_adjust_settings=AUTO_ADJUST_SETTINGS)
    p.gridlines()

    filename = DATA_PATH / "horizon-north-celestial-pole.png"
    p.export(filename)
    return filename
