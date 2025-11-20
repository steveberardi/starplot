from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

from starplot import styles, HorizonPlot, _, Observer, Star

HERE = Path(__file__).resolve().parent
DATA_PATH = HERE / "data"

STYLE = styles.PlotStyle().extend(
    styles.extensions.BLUE_MEDIUM,
    styles.extensions.MAP,
)

RESOLUTION = 4096

AUTO_ADJUST_SETTINGS = {"seed": 1}

TZ_PT = ZoneInfo("US/Pacific")


def _horizon():
    dt = datetime(2024, 8, 30, 21, 0, 0, 0, tzinfo=TZ_PT)
    observer = Observer(
        lat=36.606111,  # Lone Pine, California
        lon=-118.079444,
        dt=dt,
    )

    p = HorizonPlot(
        altitude=(0, 50),
        azimuth=(150, 210),
        observer=observer,
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
    dt = datetime(2024, 8, 30, 21, 0, 0, 0, tzinfo=TZ_PT)
    observer = Observer(
        lat=36.606111,  # Lone Pine, California
        lon=-118.079444,
        dt=dt,
    )

    p = HorizonPlot(
        altitude=(0, 50),
        azimuth=(330, 390),
        observer=observer,
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

    polaris = Star.get(name="Polaris")
    p.arrow(target=(polaris.ra, polaris.dec))

    filename = DATA_PATH / "horizon-north-celestial-pole.png"
    p.export(filename)
    return filename


def check_horizon_gradient_background():
    dt = datetime(2024, 8, 30, 21, 0, 0, 0, tzinfo=TZ_PT)
    p = HorizonPlot(
        altitude=(0, 50),
        azimuth=(150, 210),
        observer=Observer(
            lat=36.606111,  # Lone Pine, California
            lon=-118.079444,
            dt=dt,
        ),
        style=styles.PlotStyle().extend(
            styles.extensions.BLUE_GOLD,
            styles.extensions.GRADIENT_PRE_DAWN,
            styles.extensions.MAP,
        ),
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

    filename = DATA_PATH / "horizon-gradient-background.png"
    p.export(filename)
    return filename
