from pathlib import Path
from datetime import datetime

import numpy as np
from pytz import timezone

from starplot import styles, DSO, Moon
from starplot.map import MapPlot, Projection

HERE = Path(__file__).resolve().parent
DATA_PATH = HERE / "data"
STYLE = styles.PlotStyle().extend(
    styles.extensions.BLUE_LIGHT,
    styles.extensions.MAP,
)
RESOLUTION = 3200

dt_dec_16 = datetime.now(timezone("US/Pacific")).replace(2023, 12, 16, 21, 0, 0)


def _mercator():
    # returns a mercator plot of Orion
    p = MapPlot(
        projection=Projection.MERCATOR,
        ra_min=3.6,
        ra_max=7.8,
        dec_min=-16,
        dec_max=23.6,
        style=STYLE,
        resolution=RESOLUTION,
    )
    p.stars(mag=7.6, bayer_labels=True)
    p.dsos(
        labels=None,
        where=[
            DSO.magnitude.is_null() | (DSO.magnitude <= 8),
            DSO.size.is_not_null(),
            DSO.size > 0.1,
        ],
    )
    p.milky_way()
    p.gridlines()
    p.ecliptic()
    p.celestial_equator()
    p.constellations()
    p.constellation_borders()
    return p


mercator_base = _mercator()


def _stereo_north():
    p = MapPlot(
        projection=Projection.STEREO_NORTH,
        ra_min=17,
        ra_max=20,
        dec_min=30,
        dec_max=55,
        style=STYLE,
        resolution=RESOLUTION,
    )
    p.stars(mag=9, bayer_labels=True)
    p.dsos(mag=8, labels=None)
    p.milky_way()
    p.gridlines()
    p.constellations()
    p.constellation_borders()
    return p


def check_map_orion_base():
    filename = DATA_PATH / "map-orion-base.png"
    mercator_base.export(filename)
    return filename


def check_map_orion_extra():
    filename = DATA_PATH / "map-orion-extra.png"
    mercator_base.marker(
        ra=4.5,
        dec=5,
        label="hello worldzz label offset",
        style={
            "marker": {
                "size": 30,
                "symbol": "square",
                "fill": "full",
                "color": "#ff6868",
            },
            "label": {
                "offset_x": 50,
                "offset_y": -100,
            },
        },
        legend_label="hello legend",
    )
    mercator_base.circle(
        (7, -10),
        5,
        style=styles.PolygonStyle(
            fill_color="blue",
            alpha=0.14,
        ),
    )
    mercator_base.legend()
    mercator_base.export(filename, padding=0.5)
    return filename


def check_map_coma_berenices_dso_size():
    filename = DATA_PATH / "map-coma-berenices-dso-size.png"
    p = MapPlot(
        projection=Projection.MILLER,
        ra_min=12,
        ra_max=13.5,
        dec_min=15,
        dec_max=32,
        style=styles.PlotStyle().extend(
            styles.extensions.BLUE_DARK,
            styles.extensions.MAP,
        ),
        resolution=RESOLUTION,
    )
    p.stars(mag=8, bayer_labels=True)
    p.galaxies(mag=11, true_size=False)
    p.open_clusters(mag=11, true_size=True)
    p.gridlines()
    p.ecliptic()
    p.celestial_equator()
    p.constellations()
    p.constellation_borders()
    p.export(filename, padding=0.5)
    return filename


def check_map_stereo_base():
    filename = DATA_PATH / "map-stereo-north-base.png"
    map_stereo_north = _stereo_north()
    map_stereo_north.export(filename)
    return filename


def check_map_with_planets():
    filename = DATA_PATH / "map-mercator-planets.png"
    dt = timezone("UTC").localize(datetime(2023, 8, 27, 23, 0, 0, 0))

    p = MapPlot(
        projection=Projection.MILLER,
        ra_min=0,
        ra_max=24,
        dec_min=-40,
        dec_max=40,
        dt=dt,
        hide_colliding_labels=False,
        style=STYLE,
        resolution=RESOLUTION,
    )
    p.stars(mag=3, labels=None)
    p.planets()
    p.sun()
    p.ecliptic()
    p.export(filename)

    return filename


def check_map_scope_bino_fov():
    filename = DATA_PATH / "map-scope-bino-fov.png"
    dt = timezone("UTC").localize(datetime(2023, 8, 27, 23, 0, 0, 0))

    style = styles.PlotStyle().extend(
        styles.extensions.GRAYSCALE,
        styles.extensions.MAP,
    )

    p = MapPlot(
        projection=Projection.STEREO_NORTH,
        ra_min=52 / 15,
        ra_max=62 / 15,
        dec_min=20,
        dec_max=28,
        dt=dt,
        style=style,
        resolution=1000,
        star_catalog="tycho-1",
    )
    p.stars(mag=12)
    p.scope_fov(
        ra=3.791278,
        dec=24.105278,
        scope_focal_length=600,
        eyepiece_focal_length=14,
        eyepiece_fov=82,
    )
    p.bino_fov(ra=3.791278, dec=24.105278, fov=65, magnification=10)
    p.title("M45 :: TV-85 / 14mm @ 82deg, 10x binos @ 65deg")
    p.export(filename, padding=0.3)
    return filename


def check_map_custom_stars():
    filename = DATA_PATH / "map-custom-stars.png"

    style = styles.PlotStyle().extend(
        styles.extensions.GRAYSCALE,
        styles.extensions.MAP,
    )
    style.star.marker.symbol = "star_8"
    style.star.marker.size = 60

    p = MapPlot(
        projection=Projection.MERCATOR,
        ra_min=3.6,
        ra_max=7.8,
        dec_min=-16,
        dec_max=24,
        style=style,
        resolution=RESOLUTION,
    )
    p.stars(mag=6)
    p.text(
        "CUSTOM STARZZZ",
        7,
        -5,
        style={"font_size": 20, "offset_x": 40, "offset_y": 100},
    )
    p.export(filename, padding=0.3)
    return filename


def check_map_wrapping():
    filename = DATA_PATH / "map-wrapping.png"

    style = styles.PlotStyle().extend(
        styles.extensions.GRAYSCALE,
        styles.extensions.MAP,
    )

    p = MapPlot(
        projection=Projection.STEREO_NORTH,
        ra_min=18,
        ra_max=26,
        dec_min=30,
        dec_max=64,
        style=style,
        resolution=RESOLUTION,
    )
    p.stars(mag=9, style={"marker": {"size": 40}})
    p.dsos(
        where=[
            DSO.magnitude.is_null() | (DSO.magnitude < 9),
            DSO.size.is_not_null(),
            DSO.size > 0.1,
        ],
    )
    p.gridlines()
    p.constellations()
    p.title("Andromeda + nebula + Vega")
    p.export(filename, padding=0.3)
    return filename


def check_map_mollweide():
    filename = DATA_PATH / "map-mollweide.png"

    style = styles.PlotStyle().extend(
        styles.extensions.GRAYSCALE,
        styles.extensions.MAP,
    )

    p = MapPlot(
        projection=Projection.MOLLWEIDE,
        style=style,
        resolution=RESOLUTION,
    )
    p.stars(mag=4.2, mag_labels=1.8, style__marker__color="blue")
    p.constellations()
    p.dsos(mag=4, labels=None)
    p.milky_way()
    p.gridlines(labels=False)
    p.export(filename, padding=0.1)
    return filename


def check_map_gridlines():
    filename = DATA_PATH / "map-gridlines.png"

    style = styles.PlotStyle().extend(
        styles.extensions.GRAYSCALE,
        styles.extensions.MAP,
    )

    p = MapPlot(
        projection=Projection.MILLER,
        ra_min=10,
        ra_max=15,
        dec_min=31,
        dec_max=67,
        style=style,
        resolution=RESOLUTION,
    )

    p.stars(mag=6, style__marker__size=45)

    p.gridlines(tick_marks=True)

    p.gridlines(
        ra_locations=list(np.arange(0, 24, 0.25)),
        ra_formatter_fn=lambda d: None,
        dec_formatter_fn=lambda d: None,
        dec_locations=list(np.arange(-90, 90, 1)),
        style__line__alpha=0.2,
    )

    p.export(filename, padding=0.3)

    return filename


def check_map_moon_phase_waxing_crescent():
    m = Moon.get(dt=dt_dec_16)
    p = m.create_map(
        height_degrees=4,
        width_degrees=4,
        projection=Projection.MILLER,
        lat=32.97,
        lon=-117.038611,
        dt=dt_dec_16,
        style=STYLE,
    )
    p.moon(
        true_size=True,
        show_phase=True,
        label=None,
    )
    filename = DATA_PATH / "map-moon-phase-waxing-crescent.png"
    p.export(filename)
    p.close_fig()
    return filename
