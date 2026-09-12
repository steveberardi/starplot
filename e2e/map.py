import random
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
from shapely import Polygon
from utils import actual_filename

from starplot import (
    DSO,
    Binoculars,
    CollisionHandler,
    Constellation,
    DsoType,
    Equidistant,
    MapPlot,
    Mercator,
    Miller,
    Mollweide,
    Moon,
    Observer,
    PlateCarree,
    Scope,
    Star,
    StereoNorth,
    StereoSouth,
    _,
    geometry,
)
from starplot.styles import PlotStyle, PolygonStyle, extensions

RESOLUTION = 4096

# shared objects for the ported hash_checks/map_checks.py functions below
STYLE = PlotStyle().extend(
    extensions.BLUE_LIGHT,
    extensions.MAP,
)

HANDLER = CollisionHandler(seed=1, allow_constellation_line_collisions=True)

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

POWAY = {"lat": 32.97, "lon": -117.038611}

utc = ZoneInfo("UTC")
tz = ZoneInfo("America/Los_Angeles")
dt_dec_16 = datetime(2023, 12, 16, 21, 0, 0, 0, tzinfo=tz)

def e2e_map_orion() -> Path:
    """Generates the Orion map plot example (examples/map_orion.py) and exports it as SVG."""
    style = PlotStyle().extend(
        extensions.BLUE_MEDIUM,
        extensions.MAP,
    )
    style.figure.padding = 40

    p = MapPlot(
        projection=Miller(),
        ra_min=3.6 * 15,
        ra_max=7.8 * 15,
        dec_min=-15.2,
        dec_max=26,
        style=style,
        resolution=RESOLUTION,
        point_label_handler=HANDLER,
    )
    p.gridlines()
    p.constellations()
    p.constellation_borders()

    p.stars(where=[_.magnitude < 5], bayer_labels=True, where_labels=[_.magnitude < 4])

    p.open_clusters(
        where=[(_.magnitude < 9) | (_.magnitude.isnull())],
        where_labels=[False],
        where_true_size=[
            _.size > 1
        ],  # only plot larger clusters as their true apparent size
    )

    p.nebula(
        where=[(_.magnitude < 9) | (_.magnitude.isnull())],
    )

    # seeded so constellation label placement (which has some randomized
    # fallback positioning) is deterministic across runs -- otherwise this
    # SVG would never byte-for-byte match itself from one export to the next
    p.constellation_labels(collision_handler=CollisionHandler(seed=1, allow_constellation_line_collisions=True))
    p.milky_way()
    p.ecliptic()
    p.legend()

    filename = actual_filename("map_orion")
    p.export(filename)
    return filename

def e2e_map_plate_caree():
    p = MapPlot(
        projection=PlateCarree(),
        style=PlotStyle().extend(
            extensions.BLUE_NIGHT,
            extensions.MAP,
        ),
        resolution=4000,
        scale=0.75,
        point_label_handler=HANDLER,
    )
    p.stars(where=[_.magnitude < 4], where_labels=[False])
    p.gridlines()
    p.ecliptic()
    p.constellations()

    filename = actual_filename("map_plate_caree")
    p.export(filename)
    return filename

def e2e_map_equidistant_tissot():

    style = PlotStyle().extend(
        extensions.STARPLOT,
        extensions.MAP,
    )
    style.axes.border.width = 2
    style.axes.border.stroke = "#153358CA"
    style.axes.background.fill = "#2E343B"
    style.figure.background.fill = None
    style.tissot.fill = "#4476B3E4"

    p = MapPlot(
        projection=Equidistant(),
        style=style,
        resolution=RESOLUTION,
        # radius capped at 90 degrees -- MapPlot's clip_path pipeline can't
        # yet correctly render a clip_path spanning the whole sphere
        clip_path=geometry.circle(
            center=(180, 0),
            diameter_degrees=179,
            num_pts=200,
        ),
    )
    p.gridlines()
    p.tissot()

    filename = actual_filename("map_eq_tissot")
    p.export(filename)
    return filename


def _mercator():
    p = MapPlot(
        projection=Mercator(),
        ra_min=3.6 * 15,
        ra_max=7.8 * 15,
        dec_min=-16,
        dec_max=23.6,
        style=STYLE,
        resolution=RESOLUTION,
        autoscale=True,
        point_label_handler=HANDLER,
    )
    p.constellations()
    p.stars(where=[_.magnitude < 7.6], bayer_labels=True)
    p.dsos(
        where=[
            (_.magnitude.isnull()) | (_.magnitude < 9),
            _.type.isin(BASIC_DSO_TYPES),
        ],
        where_labels=[False],
        where_true_size=[_.size > 1],
    )
    p.milky_way()
    p.gridlines()
    p.ecliptic()
    p.celestial_equator()
    p.constellation_borders()
    p.constellation_labels(collision_handler=HANDLER)
    return p


mercator_base = _mercator()


def _stereo_north():
    p = MapPlot(
        projection=StereoNorth(),
        ra_min=17 * 15,
        ra_max=20 * 15,
        dec_min=30,
        dec_max=55,
        style=STYLE,
        resolution=RESOLUTION,
        autoscale=True,
        point_label_handler=HANDLER,
    )
    p.stars(
        sql="select * from _ where magnitude < 7",
        bayer_labels=True,
    )
    p.dsos(
        where=[
            (_.magnitude.isnull()) | (_.magnitude <= 9),
            _.type.isin(BASIC_DSO_TYPES),
        ],
        where_labels=False,
        where_true_size=False,
    )
    p.milky_way()
    p.gridlines()
    p.constellations()
    p.constellation_borders()
    p.constellation_labels(collision_handler=HANDLER)
    return p


def e2e_map_orion_base() -> Path:
    filename = actual_filename("map_orion_base")
    mercator_base.export(filename)
    return filename


def e2e_map_orion_extra() -> Path:
    random.seed(12)

    mercator_base.marker(
        ra=4.5 * 15,
        dec=5,
        style={
            "marker": {
                "size": 30,
                "symbol": "square",
                "fill": "#ff6868",
            },
            "label": {
                "offset_x": 50,
                "offset_y": -100,
            },
        },
        label="hello worldzz label offset",
        legend_label="hello legend",
    )
    mercator_base.arrow(
        target=(4.5 * 15, 5),
    )

    mercator_base.circle(
        (7 * 15, -10),
        5,
        style=PolygonStyle(
            fill="blue",
            opacity=0.14,
        ),
        legend_label="blue circle",
    )

    alhena = Star.get(name="Alhena")
    ain = Star.get(name="Ain")
    mercator_base.arrow(
        origin=(alhena.ra, alhena.dec),
        target=(ain.ra, ain.dec),
        style__head_width=50,
        style__body_width=20,
    )

    mercator_base.legend()

    filename = actual_filename("map_orion_extra")
    mercator_base.export(filename)
    return filename


def e2e_map_coma_berenices_dso_size() -> Path:
    p = MapPlot(
        projection=Miller(),
        ra_min=12 * 15,
        ra_max=13.5 * 15,
        dec_min=15,
        dec_max=32,
        style=PlotStyle().extend(
            extensions.BLUE_DARK,
            extensions.MAP,
        ),
        resolution=RESOLUTION,
        scale=1.5,
        point_label_handler=HANDLER,
    )
    p.stars(where=[_.magnitude < 8], bayer_labels=True)
    p.open_clusters(where=[(_.magnitude < 8) | (_.magnitude.isnull())])
    p.gridlines()
    p.ecliptic()
    p.celestial_equator()
    p.constellations()
    p.constellation_borders()
    p.constellation_labels(collision_handler=HANDLER)

    filename = actual_filename("map_coma_berenices_dso_size")
    p.export(filename)
    return filename


def e2e_map_stereo_base() -> Path:
    map_stereo_north = _stereo_north()

    filename = actual_filename("map_stereo_base")
    map_stereo_north.export(filename)
    return filename


def e2e_map_with_planets() -> Path:
    dt = datetime(2023, 8, 27, 23, 0, 0, 0, tzinfo=utc)
    observer = Observer(dt=dt)

    p = MapPlot(
        projection=Miller(),
        ra_min=0,
        ra_max=24 * 15,
        dec_min=-40,
        dec_max=40,
        observer=observer,
        style=STYLE,
        resolution=RESOLUTION,
        autoscale=True,
        point_label_handler=HANDLER,
    )
    p.stars(where=[_.magnitude < 3], where_labels=[False])
    p.planets()
    p.sun()
    p.ecliptic()

    filename = actual_filename("map_with_planets")
    p.export(filename)
    return filename


def e2e_map_with_planets_gradient() -> Path:
    dt = datetime(2023, 8, 27, 23, 0, 0, 0, tzinfo=utc)
    observer = Observer(dt=dt)

    p = MapPlot(
        projection=Miller(),
        ra_min=0,
        ra_max=24 * 15,
        dec_min=-40,
        dec_max=40,
        observer=observer,
        style=PlotStyle().extend(
            extensions.BLUE_GOLD,
            extensions.GRADIENT_PRE_DAWN,
            extensions.MAP,
        ),
        resolution=RESOLUTION,
        autoscale=True,
        point_label_handler=HANDLER,
    )
    p.stars(where=[_.magnitude < 3], where_labels=[False])
    p.planets()
    p.sun()
    p.ecliptic()

    filename = actual_filename("map_with_planets_gradient")
    p.export(filename)
    return filename


def e2e_map_scope_bino_fov() -> Path:
    dt = datetime(2023, 8, 27, 23, 0, 0, 0, tzinfo=utc)

    scope = Scope(
        focal_length=600,
        eyepiece_focal_length=14,
        eyepiece_fov=82,
    )
    binoculars = Binoculars(
        magnification=10,
        fov=65,
    )

    style = PlotStyle().extend(
        extensions.GRAYSCALE,
        extensions.MAP,
    )

    p = MapPlot(
        projection=StereoNorth(),
        ra_min=52 / 1,
        ra_max=62 / 1,
        dec_min=20,
        dec_max=28,
        dt=dt,
        style=style,
        resolution=2000,
        scale=1,
        point_label_handler=HANDLER,
    )
    p.stars(where=[_.magnitude < 12])
    p.optic_fov(
        ra=3.791278 * 15,
        dec=24.105278,
        optic=scope,
    )
    p.optic_fov(
        ra=3.791278 * 15,
        dec=24.105278,
        optic=binoculars,
    )
    p.title("M45 :: TV-85 / 14mm @ 82deg, 10x binos @ 65deg")

    filename = actual_filename("map_scope_bino_fov")
    p.export(filename)
    return filename


def e2e_map_custom_stars() -> Path:
    style = PlotStyle().extend(
        extensions.GRAYSCALE,
        extensions.MAP,
    )
    style.star.marker.symbol = "star_8"
    style.star.marker.size = 60

    p = MapPlot(
        projection=Mercator(),
        ra_min=3.6 * 15,
        ra_max=7.8 * 15,
        dec_min=-16,
        dec_max=24,
        style=style,
        resolution=RESOLUTION,
        autoscale=True,
        point_label_handler=HANDLER,
    )
    p.stars(where=[_.magnitude < 6])
    p.text(
        "CUSTOM STARZZZ",
        7 * 15,
        -5,
        style={"font_size": 20, "offset_x": 40, "offset_y": 100},
    )

    filename = actual_filename("map_custom_stars")
    p.export(filename)
    return filename


def e2e_map_wrapping() -> Path:
    style = PlotStyle().extend(
        extensions.GRAYSCALE,
        extensions.MAP,
    )

    p = MapPlot(
        projection=StereoNorth(center_ra=330),
        ra_min=18 * 15,
        ra_max=26 * 15,
        dec_min=30,
        dec_max=64,
        style=style,
        resolution=RESOLUTION,
        autoscale=True,
        point_label_handler=HANDLER,
    )
    p.stars(where=[_.magnitude < 7])
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
    p.constellation_labels(collision_handler=HANDLER)
    p.title("Andromeda + nebula + Vega")

    filename = actual_filename("map_wrapping")
    p.export(filename)
    return filename


def e2e_map_mollweide() -> Path:
    style = PlotStyle().extend(
        extensions.GRAYSCALE,
        extensions.MAP,
    )

    p = MapPlot(
        projection=Mollweide(),
        style=style,
        resolution=RESOLUTION,
        autoscale=True,
        point_label_handler=HANDLER,
    )
    p.stars(
        where=[_.magnitude < 4.2],
        where_labels=[_.magnitude < 1.8],
        style__marker__fill="blue",
    )
    p.constellations()
    p.dsos(
        where=[
            (_.magnitude.isnull()) | (_.magnitude <= 4),
            _.size.notnull(),
            _.size > 0.1,
            _.type.isin(BASIC_DSO_TYPES),
        ],
        where_labels=False,
        where_true_size=False,
    )
    p.milky_way()
    p.gridlines(labels=False)

    filename = actual_filename("map_mollweide")
    p.export(filename)
    return filename


def e2e_map_gridlines() -> Path:
    style = PlotStyle().extend(
        extensions.GRAYSCALE,
        extensions.MAP,
    )

    p = MapPlot(
        projection=Miller(),
        ra_min=10 * 15,
        ra_max=15 * 15,
        dec_min=31,
        dec_max=67,
        style=style,
        resolution=RESOLUTION,
        autoscale=True,
        point_label_handler=HANDLER,
    )

    p.stars(where=[_.magnitude < 6], style__marker__size=45)

    p.gridlines()
    p.gridlines(
        ra_locations=list(np.arange(10 * 15, 15 * 15, 3.75)),
        dec_locations=list(np.arange(20, 75, 1)),
        ra_label_fn=lambda d: None,
        dec_label_fn=lambda d: None,
        style__line__opacity=0.2,
    )

    filename = actual_filename("map_gridlines")
    p.export(filename)
    return filename


def e2e_map_moon_phase_waxing_crescent() -> Path:
    observer = Observer(
        **POWAY,
        dt=dt_dec_16,
    )
    m = Moon.get(observer)
    p = m.create_map(
        height_degrees=2,
        width_degrees=2,
        projection=Miller(),
        observer=observer,
        style=STYLE,
        autoscale=True,
        point_label_handler=HANDLER,
    )
    p.moon(
        true_size=True,
        show_phase=True,
        label=None,
    )
    ra_locations = list(np.arange(m.ra - 2, m.ra + 2, 0.5))
    dec_locations = list(np.arange(m.dec - 2, m.dec + 2, 0.5))
    p.gridlines(
        ra_locations=ra_locations,
        dec_locations=dec_locations,
        labels=False,
        style__line__opacity=1,
    )

    filename = actual_filename("map_moon_phase_waxing_crescent")
    p.export(filename)
    return filename


def e2e_map_plot_limit_by_geometry() -> Path:
    p = MapPlot(
        projection=StereoNorth(),
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
        point_label_handler=HANDLER,
    )
    lyra = Constellation.get(iau_id="lyr")

    p.stars(
        where=[_.magnitude < 9, _.geometry.intersects(lyra.boundary)], bayer_labels=True
    )
    p.dsos(
        where=[
            (_.magnitude.isnull()) | (_.magnitude < 9),
            _.type.isin(BASIC_DSO_TYPES),
            _.geometry.intersects(lyra.boundary),
        ],
        where_labels=[False],
        where_true_size=[False],
    )
    p.constellations(where=[_.boundary.intersects(lyra.boundary)])
    p.constellation_borders()
    p.constellation_labels(collision_handler=HANDLER)

    filename = actual_filename("map_plot_limit_by_geometry")
    p.export(filename)
    return filename


def e2e_map_plot_custom_clip_path_virgo() -> Path:
    virgo = Constellation.get(iau_id="vir")
    p = MapPlot(
        projection=Miller(),
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
        point_label_handler=HANDLER,
    )

    p.stars(where=[_.magnitude < 9], bayer_labels=True)
    p.dsos(
        where=[
            (_.magnitude.isnull()) | (_.magnitude < 9),
            _.type.isin(BASIC_DSO_TYPES),
        ],
        where_labels=[False],
        where_true_size=[False],
    )
    p.constellations()
    p.constellation_borders()
    p.constellation_labels(collision_handler=HANDLER)

    p.line(
        coordinates=[
            (13 * 15, 10),
            (13.42 * 15, -11.1613),  # Spica
        ],
        style__line={
            "stroke": "red",
            "width": 9,
        },
    )

    filename = actual_filename("map_plot_custom_clip_path_virgo")
    p.export(filename)
    return filename


def e2e_map_label_callables() -> Path:
    p = MapPlot(
        projection=Miller(),
        ra_min=3.5 * 15,
        ra_max=4 * 15,
        dec_min=22,
        dec_max=26,
        style=STYLE,
        scale=1.5,
        point_label_handler=HANDLER,
    )
    m45 = DSO.get(m="45")

    p.polygon(
        geometry=m45.geometry,
        style__fill=STYLE.dso_open_cluster.marker.fill,
        style__stroke="red",
        style__stroke_width=16,
        style__dash_array=(8, 32),
    )

    p.stars(
        label_fn=lambda s: str(int(s.hip)) if s.hip else None,
        where=[_.magnitude < 9.6, _.geometry.intersects(m45.geometry)],
        where_labels=[_.magnitude < 5],
        style__label__font_size=36,
    )

    filename = actual_filename("map_label_callables")
    p.export(filename)
    return filename


def e2e_map_milky_way_multi_polygon() -> Path:
    p = MapPlot(
        projection=Miller(),
        ra_min=17.5 * 15,
        ra_max=19.5 * 15,
        dec_min=-30,
        dec_max=0,
        style=STYLE,
        resolution=3000,
        scale=1.4,
        point_label_handler=HANDLER,
    )
    p.stars(where=[_.magnitude < 6], bayer_labels=True)
    p.constellations()
    p.milky_way()

    filename = actual_filename("map_milky_way_multi_polygon")
    p.export(filename)
    return filename


def e2e_map_allow_all_collisions() -> Path:
    handler = CollisionHandler(
        seed=1,
        allow_clipped=True,
        allow_label_collisions=True,
        allow_marker_collisions=True,
        allow_constellation_line_collisions=True,
        plot_on_fail=True,
    )
    p = MapPlot(
        projection=Miller(),
        ra_min=17.5 * 15,
        ra_max=19.5 * 15,
        dec_min=-30,
        dec_max=-20,
        style=STYLE,
        resolution=3000,
        scale=1.5,
        point_label_handler=handler,
    )
    p.stars(where=[_.magnitude < 6], bayer_labels=True, flamsteed_labels=True)
    p.dsos(where=[_.magnitude < 10], where_true_size=[False])

    filename = actual_filename("map_allow_all_collisions")
    p.export(filename)
    return filename


def e2e_map_allow_marker_and_line_collisions() -> Path:
    handler = CollisionHandler(
        seed=1,
        allow_marker_collisions=True,
        allow_constellation_line_collisions=True,
        plot_on_fail=True,
    )
    p = MapPlot(
        projection=Miller(),
        ra_min=17.5 * 15,
        ra_max=19.5 * 15,
        dec_min=-30,
        dec_max=-10,
        style=STYLE,
        resolution=3000,
        scale=1.5,
        point_label_handler=handler,
    )
    p.constellations()
    p.stars(where=[_.magnitude < 8], bayer_labels=True, flamsteed_labels=True)
    p.dsos(where=[_.magnitude < 10], where_true_size=[False])

    filename = actual_filename("map_allow_marker_and_line_collisions")
    p.export(filename)
    return filename


def e2e_map_constellation_clip_path() -> Path:
    constellation = Constellation.get(iau_id="and")

    ra, dec = [c for c in constellation.border.coords.xy]
    extent = (min(ra) - 2, max(min(dec) - 2, -90), max(ra) + 2, min(max(dec) + 2, 90))

    if constellation.dec > 60:
        proj = StereoNorth
    elif constellation.dec < -60:
        proj = StereoSouth
    else:
        proj = Miller

    if extent[0] < 0:
        extent = (extent[0] + 360, extent[1], extent[2] + 360, extent[3])

    center_ra = (extent[0] + extent[2]) / 2
    if center_ra < 0:
        center_ra += 360
    elif center_ra > 360:
        center_ra -= 360

    p = MapPlot(
        projection=proj(center_ra=center_ra),
        ra_min=extent[0],
        ra_max=extent[2],
        dec_min=extent[1],
        dec_max=extent[3],
        style=PlotStyle().extend(
            extensions.BLUE_NIGHT,
            extensions.MAP,
        ),
        clip_path=Polygon(constellation.border.coords),
        resolution=2000,
        scale=0.8,
        point_label_handler=HANDLER,
    )

    p.line(
        geometry=constellation.border,
        style__line=p.style.constellation_borders,
    )

    for hip1, hip2 in constellation.star_hip_lines:
        star1 = Star.get(hip=hip1)
        star2 = Star.get(hip=hip2)
        p.line(
            coordinates=[
                (star1.ra, star1.dec),
                (star2.ra, star2.dec),
            ],
            style__line=p.style.constellation_lines,
        )

    p.stars(
        where=[_.hip.isin(constellation.star_hip_ids)],
        where_labels=[_.magnitude < 4],
        bayer_labels=True,
    )

    p.title(constellation.name)

    filename = actual_filename("map_constellation_clip_path")
    p.export(filename)
    return filename


def e2e_map_font_fallback() -> Path:
    style = PlotStyle().extend(
        extensions.GRAYSCALE,
        extensions.MAP,
    )
    style.title.font_name = "ThisFontDoesNotExist12345"
    style.constellation_labels.font_name = "AlsoNotARealFont"

    p = MapPlot(
        projection=Miller(),
        ra_min=3.6 * 15,
        ra_max=7.8 * 15,
        dec_min=-16,
        dec_max=23.6,
        style=style,
        resolution=RESOLUTION,
        autoscale=True,
        point_label_handler=HANDLER,
    )
    p.constellations()
    p.constellation_labels()
    p.stars(where=[_.magnitude < 6])
    p.title("Font Fallback Test")

    filename = actual_filename("map_font_fallback")
    p.export(filename)
    return filename
