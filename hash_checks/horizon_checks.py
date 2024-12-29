import random

from pathlib import Path
from datetime import datetime

from pytz import timezone

from starplot import styles, DSO, Star, HorizonPlot

random.seed(1)

HERE = Path(__file__).resolve().parent
DATA_PATH = HERE / "data"

STYLE = styles.PlotStyle().extend(
    styles.extensions.BLUE_MEDIUM,
    styles.extensions.MAP,
)

RESOLUTION = 4096


def _horizon():
    dt = timezone("US/Pacific").localize(datetime(2024, 8, 30, 21, 0, 0, 0))

    p = HorizonPlot(
        altitude=(0, 60),
        azimuth=(175, 275),
        lat=36.606111,  # Lone Pine, California
        lon=-118.079444,
        dt=dt,
        style=STYLE,
        resolution=RESOLUTION,
        scale=0.9,
    )
    p.constellations()
    p.constellation_borders()
    p.milky_way()
    p.stars(where=[Star.magnitude < 5])
    p.messier(where=[DSO.magnitude < 12], true_size=False, label_fn=lambda d: f"M{d.m}")
    p.planets()
    p.ecliptic()
    p.horizon()
    p.constellation_labels()
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
        altitude=(0, 70),
        azimuth=(310, 410),
        lat=36.606111,  # Lone Pine, California
        lon=-118.079444,
        dt=dt,
        style=STYLE,
        resolution=RESOLUTION,
        scale=0.9,
    )
    p.constellations()
    p.constellation_borders()
    p.milky_way()
    p.stars(where=[Star.magnitude < 5])
    p.messier(where=[DSO.magnitude < 12], true_size=False, label_fn=lambda d: f"M{d.m}")
    p.planets()
    p.ecliptic()
    p.horizon()
    p.constellation_labels()
    p.gridlines()

    filename = DATA_PATH / "horizon-north-celestial-pole.png"
    p.export(filename)
    return filename
