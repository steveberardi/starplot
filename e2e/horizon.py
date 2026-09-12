import random
from datetime import datetime
from zoneinfo import ZoneInfo

from utils import actual_filename

from starplot import CollisionHandler, HorizonPlot, Observer, Star, _, styles

STYLE = styles.PlotStyle().extend(
    styles.extensions.BLUE_MEDIUM,
    styles.extensions.HORIZON,
)

RESOLUTION = 4096

SEED = 23

HANDLER = CollisionHandler(seed=1, allow_constellation_line_collisions=True)

TZ_PT = ZoneInfo("US/Pacific")


def _horizon():
    random.seed(SEED)
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
    p.ground(
        style__fill={
            "stops": styles.gradients.GROUND,
            "type": "linear",
        },
    )
    p.constellations()
    p.constellation_borders()
    p.milky_way()
    p.stars(where=[_.magnitude < 5])
    p.messier(where_true_size=[_.size > 1])
    p.ecliptic()
    p.constellation_labels(collision_handler=HANDLER)
    p.gridlines()
    return p


def e2e_horizon_base():
    horizon_base = _horizon()
    filename = actual_filename("horizon_base")
    horizon_base.export(filename)
    return filename


def e2e_horizon_north_celestial_pole():
    random.seed(SEED)
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
    p.messier(where_true_size=[_.size > 1])
    p.ecliptic()
    p.constellation_labels(collision_handler=HANDLER)
    p.gridlines()

    polaris = Star.get(name="Polaris")
    p.arrow(target=(polaris.ra, polaris.dec))

    filename = actual_filename("horizon_north_celestial_pole")
    p.export(filename)
    return filename


def e2e_horizon_gradient_background():
    random.seed(SEED)
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
            styles.extensions.HORIZON,
        ),
        resolution=RESOLUTION,
        scale=1,
    )
    p.ground(
        style__fill={
            "stops": styles.gradients.GROUND,
            "type": "linear",
        },
    )
    p.constellations()
    p.constellation_borders()
    p.milky_way()
    p.stars(where=[_.magnitude < 5])
    p.ecliptic()
    p.constellation_labels(collision_handler=HANDLER)
    p.gridlines()

    filename = actual_filename("horizon_gradient_background")
    p.export(filename)
    return filename
