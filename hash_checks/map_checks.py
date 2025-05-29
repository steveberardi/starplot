from pathlib import Path
from datetime import datetime

import numpy as np
from pytz import timezone

from starplot import styles, DSO, DsoType, Moon, Constellation, _
from starplot.map import MapPlot, Projection

HERE = Path(__file__).resolve().parent
DATA_PATH = HERE / "data"
STYLE = styles.PlotStyle().extend(
    styles.extensions.BLUE_LIGHT,
    styles.extensions.MAP,
)
RESOLUTION = 3200

POWAY = {"lat": 32.97, "lon": -117.038611}

AUTO_ADJUST_SETTINGS = {"seed": 1}

BASIC_DSO_TYPES = [
    # Star Clusters ----------
    DsoType.OPEN_CLUSTER.value,
    DsoType.GLOBULAR_CLUSTER.value,
    # Galaxies ----------
    DsoType.GALAXY.value,
    DsoType.GALAXY_PAIR.value,
    DsoType.GALAXY_TRIPLET.value,
    DsoType.GROUP_OF_GALAXIES.value,
    # Nebulas ----------
    DsoType.NEBULA.value,
    DsoType.PLANETARY_NEBULA.value,
    DsoType.EMISSION_NEBULA.value,
    DsoType.STAR_CLUSTER_NEBULA.value,
    DsoType.REFLECTION_NEBULA.value,
    # Stars ----------
    DsoType.ASSOCIATION_OF_STARS.value,
]

dt_dec_16 = datetime.now(timezone("US/Pacific")).replace(2023, 12, 16, 21, 0, 0)


def _mercator():
    # returns a mercator plot of Orion
    p = MapPlot(
        projection=Projection.MERCATOR,
        ra_min=3.6 * 15,
        ra_max=7.8 * 15,
        dec_min=-16,
        dec_max=23.6,
        style=STYLE,
        resolution=RESOLUTION,
        autoscale=True,
    )
    p.constellations()
    p.stars(where=[_.magnitude < 7.6], bayer_labels=True)
    p.dsos(
        labels=None,
        where=[
            (_.magnitude.isnull()) | (_.magnitude <= 8),
            _.size.notnull(),
            _.size > 0.1,
            _.type.isin(BASIC_DSO_TYPES),
        ],
    )
    p.milky_way()
    p.gridlines()
    p.ecliptic()
    p.celestial_equator()
    p.constellation_borders()
    p.constellation_labels(auto_adjust_settings=AUTO_ADJUST_SETTINGS)
    return p


mercator_base = _mercator()


def _stereo_north():
    p = MapPlot(
        projection=Projection.STEREO_NORTH,
        ra_min=17 * 15,
        ra_max=20 * 15,
        dec_min=30,
        dec_max=55,
        style=STYLE,
        resolution=RESOLUTION,
        autoscale=True,
    )
    p.stars(
        sql="select * from _ where magnitude < 9",
        bayer_labels=True,
    )
    p.dsos(
        labels=None,
        true_size=False,
        where=[
            (_.magnitude.isnull()) | (_.magnitude <= 9),
            _.type.isin(BASIC_DSO_TYPES),
        ],
    )
    p.milky_way()
    p.gridlines()
    p.constellations()
    p.constellation_borders()
    p.constellation_labels(auto_adjust_settings=AUTO_ADJUST_SETTINGS)
    return p


def check_map_orion_base():
    filename = DATA_PATH / "map-orion-base.png"
    mercator_base.export(filename)
    return filename


def check_map_orion_extra():
    filename = DATA_PATH / "map-orion-extra.png"
    mercator_base.marker(
        ra=4.5 * 15,
        dec=5,
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
        label="hello worldzz label offset",
        legend_label="hello legend",
    )
    mercator_base.circle(
        (7 * 15, -10),
        5,
        style=styles.PolygonStyle(
            fill_color="blue",
            alpha=0.14,
        ),
        legend_label="blue circle",
    )
    mercator_base.legend()
    mercator_base.export(filename, padding=0.5)
    return filename


def check_map_coma_berenices_dso_size():
    filename = DATA_PATH / "map-coma-berenices-dso-size.png"
    p = MapPlot(
        projection=Projection.MILLER,
        ra_min=12 * 15,
        ra_max=13.5 * 15,
        dec_min=15,
        dec_max=32,
        style=styles.PlotStyle().extend(
            styles.extensions.BLUE_DARK,
            styles.extensions.MAP,
        ),
        resolution=RESOLUTION,
        scale=1.5,
    )
    p.stars(where=[_.magnitude < 8], bayer_labels=True)
    p.open_clusters(where=[(_.magnitude < 8) | (_.magnitude.isnull())], true_size=True)
    p.gridlines()
    p.ecliptic()
    p.celestial_equator()
    p.constellations()
    p.constellation_borders()
    p.constellation_labels(auto_adjust_settings=AUTO_ADJUST_SETTINGS)
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
        ra_max=24 * 15,
        dec_min=-40,
        dec_max=40,
        dt=dt,
        hide_colliding_labels=False,
        style=STYLE,
        resolution=RESOLUTION,
        autoscale=True,
    )
    p.stars(where=[_.magnitude < 3], where_labels=[False])
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
        ra_min=52 / 1,
        ra_max=62 / 1,
        dec_min=20,
        dec_max=28,
        dt=dt,
        style=style,
        resolution=2000,
        star_catalog="big-sky-mag11",
        scale=1,
    )
    p.stars(where=[_.magnitude < 12])
    p.scope_fov(
        ra=3.791278 * 15,
        dec=24.105278,
        scope_focal_length=600,
        eyepiece_focal_length=14,
        eyepiece_fov=82,
    )
    p.bino_fov(ra=3.791278 * 15, dec=24.105278, fov=65, magnification=10)
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
        ra_min=3.6 * 15,
        ra_max=7.8 * 15,
        dec_min=-16,
        dec_max=24,
        style=style,
        resolution=RESOLUTION,
        autoscale=True,
    )
    p.stars(where=[_.magnitude < 6])
    p.text(
        "CUSTOM STARZZZ",
        7 * 15,
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
        ra_min=18 * 15,
        ra_max=26 * 15,
        dec_min=30,
        dec_max=64,
        style=style,
        resolution=RESOLUTION,
        autoscale=True,
    )
    p.stars(where=[_.magnitude < 9])
    p.dsos(
        where=[
            (_.magnitude.isnull()) | (_.magnitude < 9),
            _.type.isin(BASIC_DSO_TYPES),
            _.size.notnull(),
            _.size > 0.1,
        ],
    )
    p.gridlines()
    p.constellations()
    p.constellation_labels(auto_adjust_settings=AUTO_ADJUST_SETTINGS)
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
        autoscale=True,
    )
    p.stars(
        where=[_.magnitude < 4.2],
        where_labels=[_.magnitude < 1.8],
        style__marker__color="blue",
    )
    p.constellations()
    p.dsos(
        labels=None,
        where=[
            (_.magnitude.isnull()) | (_.magnitude <= 4),
            _.size.notnull(),
            _.size > 0.1,
            _.type.isin(BASIC_DSO_TYPES),
        ],
    )
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
        ra_min=10 * 15,
        ra_max=15 * 15,
        dec_min=31,
        dec_max=67,
        style=style,
        resolution=RESOLUTION,
        autoscale=True,
    )

    p.stars(where=[_.magnitude < 6], style__marker__size=45)

    p.gridlines(tick_marks=True)

    p.gridlines(
        ra_locations=list(np.arange(0, 360, 3.75)),
        ra_formatter_fn=lambda d: None,
        dec_formatter_fn=lambda d: None,
        dec_locations=list(np.arange(-90, 90, 1)),
        style__line__alpha=0.2,
    )

    p.export(filename, padding=0.3)

    return filename


def check_map_moon_phase_waxing_crescent():
    m = Moon.get(dt=dt_dec_16, **POWAY)
    p = m.create_map(
        height_degrees=4,
        width_degrees=4,
        projection=Projection.MILLER,
        **POWAY,
        dt=dt_dec_16,
        style=STYLE,
        autoscale=True,
    )
    p.moon(
        true_size=True,
        show_phase=True,
        label=None,
    )
    p.gridlines(
        ra_locations=list(np.arange(0, 24 * 15, 0.05 * 15)),
        ra_formatter_fn=lambda d: None,
        dec_formatter_fn=lambda d: None,
        dec_locations=list(np.arange(-90, 90, 0.25)),
        style__line__alpha=0.2,
    )
    filename = DATA_PATH / "map-moon-phase-waxing-crescent.png"
    p.export(filename)
    p.close_fig()
    return filename


def check_map_plot_limit_by_geometry():
    p = MapPlot(
        projection=Projection.STEREO_NORTH,
        ra_min=18 * 15,
        ra_max=20 * 15,
        dec_min=23,
        dec_max=50,
        style=STYLE.extend(
            {
                "dso_open_cluster": {"marker": {"size": 20}},
                "dso_galaxy": {"marker": {"size": 20}},
                "dso_nebula": {"marker": {"size": 20}},
            }
        ),
        resolution=RESOLUTION,
        autoscale=True,
    )
    lyra = Constellation.get(iau_id="lyr")

    p.stars(
        where=[_.magnitude < 9, _.geometry.intersects(lyra.boundary)], bayer_labels=True
    )
    p.dsos(
        labels=None,
        true_size=False,
        where=[
            (_.magnitude.isnull()) | (_.magnitude < 9),
            _.type.isin(BASIC_DSO_TYPES),
            _.geometry.intersects(lyra.boundary),
        ],
    )
    p.constellations(where=[_.boundary.intersects(lyra.boundary)])
    p.constellation_borders()
    p.constellation_labels(auto_adjust_settings=AUTO_ADJUST_SETTINGS)

    filename = DATA_PATH / "map-limit-by-geometry.png"
    p.export(filename)
    p.close_fig()
    return filename


def check_map_plot_custom_clip_path_virgo():
    virgo = Constellation.get(iau_id="vir")
    p = MapPlot(
        projection=Projection.MILLER,
        ra_min=11 * 15,
        ra_max=16 * 15,
        dec_min=-29,
        dec_max=17,
        style=STYLE.extend(
            {
                "dso_open_cluster": {"marker": {"size": 20}},
                "dso_galaxy": {"marker": {"size": 20}},
            }
        ),
        resolution=RESOLUTION,
        autoscale=True,
        clip_path=virgo.boundary,
    )

    p.stars(where=[_.magnitude < 9], bayer_labels=True)
    p.dsos(
        labels=None,
        true_size=False,
        where=[
            (_.magnitude.isnull()) | (_.magnitude < 9),
            _.type.isin(BASIC_DSO_TYPES),
        ],
    )
    p.constellations()
    p.constellation_borders()
    p.constellation_labels(auto_adjust_settings=AUTO_ADJUST_SETTINGS)

    p.line(
        coordinates=[
            (13 * 15, 10),
            (13.42 * 15, -11.1613),  # Spica
        ],
        style={
            "color": "red",
            "width": 9,
        },
    )

    filename = DATA_PATH / "map-custom-clip-path-virgo.png"
    p.export(filename)
    p.close_fig()
    return filename


def check_map_label_callables():
    p = MapPlot(
        projection=Projection.MILLER,
        ra_min=3.5 * 15,
        ra_max=4 * 15,
        dec_min=22,
        dec_max=26,
        style=STYLE,
        resolution=2000,
        autoscale=True,
    )
    m45 = DSO.get(m="45")

    p.polygon(
        geometry=m45.geometry,
        style__color=None,
        style__fill_color=STYLE.dso_open_cluster.marker.color,
        style__edge_color="red",
        style__edge_width=16,
        style__line_style=(0, (4, 8)),
    )

    p.stars(
        catalog="big-sky-mag11",
        label_fn=lambda s: str(int(s.hip)) if s.hip else None,
        where=[_.magnitude < 9.6, _.geometry.intersects(m45.geometry)],
        where_labels=[_.magnitude < 5],
        style__label__font_size=36,
    )

    filename = DATA_PATH / "map-m45-label-callables.png"
    p.export(filename)
    p.close_fig()
    return filename


def check_map_milky_way_multi_polygon():
    p = MapPlot(
        projection=Projection.MILLER,
        ra_min=17.5 * 15,
        ra_max=19.5 * 15,
        dec_min=-30,
        dec_max=0,
        style=STYLE,
        resolution=3000,
        autoscale=True,
    )
    p.stars(where=[_.magnitude < 6], bayer_labels=True)
    p.constellations()
    p.milky_way()

    filename = DATA_PATH / "map-milky-way-multi-polygon.png"
    p.export(filename)
    p.close_fig()
    return filename
