"""
This file is used as a 'scratchpad' during development for testing plots.
"""

import time
from datetime import datetime

from pytz import timezone

from starplot.styles import PlotStyle, extensions, PolygonStyle, MarkerSymbolEnum
from starplot.models import SkyObject
from starplot.map import Projection
from starplot import callables

import starplot as sp

start_time = time.time()

pstyle = PolygonStyle(
    fill_color="blue",
    alpha=0.36,
    edge_width=0,
    zorder=-100,
)


def create_map_orion():
    style = PlotStyle().extend(
        # extensions.GRAYSCALE,
        # extensions.GRAYSCALE_DARK,
        extensions.BLUE_LIGHT,
        # extensions.BLUE_MEDIUM,
        # extensions.BLUE_DARK,
        extensions.MAP,
        {
            "star": {
                "label": {"font_size": 8},
            },
            "bayer_labels": {
                "font_name": "GFS Didot",
                "font_size": 7,
            },
            "legend": {
                "location": "lower right",
                "num_columns": 1,
                "background_alpha": 1,
            },
        },
    )

    p = sp.MapPlot(
        projection=Projection.MERCATOR,
        # projection=Projection.STEREO_NORTH,
        ra_min=3.4,
        ra_max=8,
        dec_min=-16,
        dec_max=25.6,
        # ra_min=0,
        # ra_max=24,
        # dec_min=40,
        # dec_max=90,
        style=style,
        resolution=3200,
        debug=True,
    )
    p.plot_stars(
        # catalog="tycho-1",
        limiting_magnitude=12,
    )
    p.plot_dsos(
        limiting_magnitude=12,
        plot_null_magnitudes=True,
    )
    
    p.plot_constellations()
    p.plot_milky_way()
    p.plot_ecliptic()

    p.plot_object(
        SkyObject(
            name="hello",
            ra=4.5,
            dec=5,
            style={
                "marker": {
                    "size": 12,
                    "symbol": MarkerSymbolEnum.CIRCLE_CROSS,
                    "fill": "full",
                    # "color": "#ff6868",
                    "color": "red",
                    "edge_color": "black",
                    "alpha": 0.7,
                    "zorder": 4096,
                },
                "label": {
                    "font_size": 12,
                    "font_weight": "bold",
                    # "font_color": "blue",
                    # "font_name": "GFS Didot",
                    "font_color": "darkred",
                    "zorder": 4096,
                },
            },
            legend_label="crossmarker",
        )
    )

    points = [
        (5 * 15, 10),
        (6 * 15, 10),
        (6 * 15, 0),
        (5 * 15, 0),
        (5 * 15, 10),
    ]

    p.plot_polygon(
        points,
        pstyle,
    )
    p.plot_rectangle(
        # (6, 20),
        # 5,
        # 10,
        (0, 70),
        10,
        10,
        style=pstyle,
        angle=0,
    )
    p.plot_circle(
        # (7, -5),
        # 5,
        # (0, 80),
        # 10,
        (0, 90),
        5,
        style=pstyle,
    )

    p.plot_ellipse(
        (6, 20),
        5,
        10,
        angle=45,
        style=pstyle,
    )

    p.plot_bino_fov(ra=5.6, dec=-1.2, fov=65, magnification=10)

    p.refresh_legend()
    # p.export("temp/map-orion.svg", format="svg", padding=1)
    p.export("temp/map-orion.png", padding=0.25)


def create_zenith():
    """Create zenith plot for tonight's sky in Poway"""
    style = PlotStyle().extend(
        # extensions.GRAYSCALE,
        # extensions.BLUE_LIGHT,
        extensions.BLUE_MEDIUM,
        # extensions.BLUE_DARK,
        extensions.ZENITH,
    )
    style.ecliptic.line.visible = True
    style.celestial_equator.line.visible = True
    p = sp.ZenithPlot(
        lat=32.97,
        lon=-117.038611,
        dt=datetime.now(timezone("America/Los_Angeles")).replace(hour=21),
        limiting_magnitude=4.6,
        # style=sp.styles.ZENITH_BLUE_MEDIUM,
        style=style,
        resolution=2000,
        include_info_text=True,
        # adjust_text=True,
    )
    # p.plot_circle(
    #     (7, -5),
    #     5,
    #     style=pstyle,
    # )
    p.plot_ecliptic()
    p.plot_celestial_equator()
    # p.refresh_legend()
    p.export("temp/zenith-poway.png", format="png", transparent=True)


def create_map_miller():
    """Create near full extent of map with miller projection"""
    style = PlotStyle().extend(
        # extensions.GRAYSCALE,
        # extensions.GRAYSCALE_DARK,
        extensions.BLUE_LIGHT,
        # extensions.BLUE_MEDIUM,
        # extensions.BLUE_DARK,
        extensions.MAP,
        {
            "bayer_labels": {
                "visible": False
                # "font_name": "GFS Didot",
                # "font_size": 7,
            },
            "constellation_borders": {"visible": True},
        },
    )

    style.star.label.font_size = 4
    style.constellation.label.font_size = 6
    style.constellation.line.width = 2
    style.legend.visible = False
    # style.milky_way.visible = False
    # style.constellation.line.visible = False
    p = sp.MapPlot(
        # projection=Projection.MERCATOR,
        projection=Projection.MILLER,
        ra_min=0,
        ra_max=24,
        dec_min=-70,
        dec_max=70,
        limiting_magnitude=6,
        style=style,
        resolution=8000,
        adjust_text=False,
    )
    p.plot_stars(limiting_magnitude=8)
    p.plot_dsos(limiting_magnitude=8, plot_null_magnitudes=True)
    # p.export("temp/map-mercator.svg", format="svg", padding=1)
    p.export("temp/map-miller.png", padding=0.3)


def create_map_stereo_north():
    style = PlotStyle().extend(
        extensions.BLUE_LIGHT,
        extensions.MAP,
    )
    p = sp.MapPlot(
        projection=Projection.STEREO_NORTH,
        ra_min=0,
        ra_max=6,
        dec_min=30,
        dec_max=80,
        limiting_magnitude=8,
        style=style,
        resolution=4000,
    )
    p.export("temp/temp-map-north.png", padding=0.5)


def create_map_stereo_south():
    p = sp.MapPlot(
        projection=Projection.STEREO_SOUTH,
        ra_min=9,
        ra_max=15,
        dec_min=-90,
        dec_max=-40,
        limiting_magnitude=8,
        style=sp.styles.MAP_BLUE_DARK,
        resolution=8000,
        adjust_text=False,
    )
    p.export("temp-map-south.svg", format="svg")


def create_map_sgr():
    style = PlotStyle().extend(
        # sp.styles.extensions.HIDE_LABELS,
        # extensions.GRAYSCALE,
        # extensions.BLUE_LIGHT,
        # extensions.BLUE_MEDIUM,
        # extensions.MINIMAL,
        extensions.HIDE_LABELS,
        extensions.BLUE_DARK,
        extensions.MAP,
        {
            "bayer_labels": {
                "font_name": "GFS Didot",
                "font_size": 8,
            },
            "constellation_borders": {"visible": False},
            "milky_way": {
                "visible": True,
                "alpha": 0.06,
            },
        },
    )
    style.ecliptic.line.visible = False
    style.legend.visible = False
    style.tick_marks.visible = False
    style.gridlines.line.visible = False

    style.constellation.line.width = 12

    style.dso_open_cluster.marker.size = 12
    style.dso_globular_cluster.marker.size = 12
    style.dso.marker.size = 12
    style.dso_galaxy.marker.size = 12
    style.dso_nebula.marker.size = 12

    p = sp.MapPlot(
        projection=Projection.STEREO_SOUTH,
        star_catalog="tycho-1",
        ra_min=17.8,
        ra_max=19.4,
        dec_min=-36,
        dec_max=-23,
        limiting_magnitude=14,
        # hide_colliding_labels=False,
        style=style,
        resolution=1200,
    )
    # p.export("temp/map-sgr.svg", format="svg", padding=0.4)
    p.export("temp/map-sgr.png", format="png", padding=0.2)


def create_scope_view_m45():
    style = PlotStyle().extend(
        # extensions.MINIMAL,
        # extensions.GRAYSCALE_DARK,
        extensions.BLUE_LIGHT,
        # extensions.BLUE_MEDIUM,
        # extensions.BLUE_DARK,
        extensions.MAP,
    )

    p = sp.MapPlot(
        # projection=Projection.MERCATOR,
        projection=Projection.STEREO_NORTH,
        ra_min=3.5,
        ra_max=4,  # 3.9
        dec_min=22,
        dec_max=26,
        limiting_magnitude=12,
        style=style,
        resolution=2000,
        star_catalog="tycho-1",
    )
    p.plot_scope_fov(
        ra=3.7836111111,
        dec=24.1166666667,
        scope_focal_length=600,
        eyepiece_focal_length=9,
        eyepiece_fov=100,
    )

    p.export("temp/map-scope-fov-m45.png", format="png", padding=0.3)


def create_scope_plot_m45():
    style = PlotStyle().extend(
        extensions.MINIMAL,
        extensions.GRAYSCALE_DARK,
        # extensions.GRAYSCALE,
        # extensions.BLUE_DARK,
        extensions.OPTIC,
    )

    p = sp.OpticPlot(
        # M45
        ra=3.7836111111,
        dec=24.1166666667,
        # owl cluster
        # ra=1.33,
        # dec=58.29,
        # double cluster
        # ra=2.33,
        # dec=57.14,
        # M35
        # ra=6.15,
        # dec=24.34,
        # Alder
        # ra=4.598667,
        # dec=16.50975,
        # Hyades
        # ra=4.501,
        # dec=15.96,
        lat=32.97,
        lon=-117.038611,
        # AT72EDII
        # optic=sp.optics.Refractor(
        #     focal_length=430,
        #     eyepiece_focal_length=11,
        #     eyepiece_fov=82,
        # ),
        # TV-85
        # optic=sp.optics.Refractor(
        #     focal_length=600,
        #     eyepiece_focal_length=9,
        #     eyepiece_fov=100,
        # ),
        # 10x binoculars
        # optic=sp.optics.Binoculars(
        #     magnification=10,
        #     fov=65,
        # ),
        # Fuji X-T1
        optic=sp.optics.Camera(
            sensor_height=15.6,
            # sensor_height=22.2,
            sensor_width=23.6,
            lens_focal_length=400,
            rotation=40,
        ),
        dt=datetime.now(timezone("America/Los_Angeles")).replace(
            hour=21, minute=30, second=0
        ),
        limiting_magnitude=14,
        style=style,
        resolution=2000,
        include_info_text=True,
        colorize_stars=True,
        # adjust_text=True,
    )

    # p.ax.set_title("M45 through 10x binoculars", fontsize=24)
    p.export("temp/scope-m45.svg", format="svg", padding=0.3)
    # p.export("temp/scope-m45.png", format="png", padding=0.3)


def create_optic_plot():
    style = PlotStyle().extend(
        # extensions.MINIMAL,
        extensions.GRAYSCALE_DARK,
        # extensions.GRAYSCALE,
        # extensions.BLUE_LIGHT,
        extensions.OPTIC,
    )
    # style.star.marker.size = 20
    # style.dso_nebula.marker.color = None

    p1 = sp.OpticPlot(
        # ra=2.3774370927640605,
        # dec=13.123794519262857,
        # M45
        # ra=3.7836111111,
        # dec=24.1166666667,
        # M44
        # ra=8.667,
        # dec=19.67,
        # star cluster near southern pole - NGC 371
        # ra=1.05,
        # dec=-72.06,
        # ra=12.1,
        # dec=-61.25,
        # double cluster
        # ra=2.33,
        # dec=57.14,
        # Hyades
        # ra=4.501,
        # dec=15.96,
        # Orion's belt
        # ra=5.6,
        # dec=-1.2,
        # Orion Nebula
        ra=5.583,
        dec=-5.383,
        lat=32.97,
        lon=-117.038611,
        # Falkland Islands
        # lat=-51.524793,
        # lon=-60.118504,
        # 10x binoculars
        optic=sp.optics.Binoculars(
            magnification=10,
            fov=65,
        ),
        # TV-85
        # optic=sp.optics.Scope(
        #     focal_length=600,
        #     eyepiece_focal_length=5,
        #     eyepiece_fov=50,
        # ),
        dt=datetime.now(timezone("America/Los_Angeles")).replace(
            hour=20, minute=30, second=0
        ),
        limiting_magnitude=9.6,
        limiting_magnitude_labels=9,
        style=style,
        resolution=1600,
        include_info_text=True,
        # colorize_stars=True,
        debug=True,
    )
    # p1.plot_circle(
    #     (3.7836111111, 24.1166666667),
    #     0.5,
    #     pstyle,
    # )
    p1.plot_stars(limiting_magnitude=9.6, color_fn=callables.color_by_bv)
    p1.plot_dsos(limiting_magnitude=4.1)

    p2 = sp.OpticPlot(
        # M45
        # ra=3.7836111111,
        # dec=24.1166666667,
        # double cluster
        ra=2.33,
        dec=57.14,
        # M44
        # ra=8.667,
        # dec=19.67,
        # Hyades
        # ra=4.501,
        # dec=15.96,
        lat=32.97,
        lon=-117.038611,
        # 10x binoculars
        # optic=sp.optics.Binoculars(
        #     magnification=10,
        #     fov=65,
        # ),
        # AT72EDII
        optic=sp.optics.Refractor(
            focal_length=430,
            eyepiece_focal_length=11,
            eyepiece_fov=82,
        ),
        # TV-85
        # optic=sp.optics.Refractor(
        #     focal_length=600,
        #     eyepiece_focal_length=9,
        #     eyepiece_fov=100,
        # ),
        # optic=sp.optics.Reflector(
        #     focal_length=600,
        #     eyepiece_focal_length=9,
        #     eyepiece_fov=100,
        # ),
        # Fuji X-T2
        # optic=sp.optics.Camera(
        #     sensor_height=15.6,
        #     sensor_width=23.6,
        #     lens_focal_length=430,
        # ),
        dt=datetime.now(timezone("America/Los_Angeles")).replace(
            hour=21, minute=0, second=0
        ),
        limiting_magnitude=12,
        style=style,
        resolution=1600,
        include_info_text=True,
        debug=True,
    )
    # p2.plot_stars(limiting_magnitude=12)
    p2.plot_info()

    # p1.export("temp/optic-p1.svg", format="svg", padding=0.3)
    # p2.export("temp/optic-p2.svg", format="svg", padding=0.3)

    p1.export("temp/optic-p1.png", padding=0.3)
    p2.export("temp/optic-p2.png", padding=0.3)


def create_constellation():
    style = PlotStyle().extend(
        extensions.GRAYSCALE,
        # extensions.BLUE_LIGHT,
        # extensions.BLUE_MEDIUM,
        extensions.MINIMAL,
        extensions.HIDE_LABELS,
        # extensions.BLUE_DARK,
        extensions.MAP,
    )
    style.ecliptic.line.visible = False
    style.legend.visible = False
    style.tick_marks.visible = False
    style.gridlines.line.visible = False

    style.star.marker.size = 50

    style.constellation.line.visible = True
    style.constellation.line.width = 8
    style.dso.marker.visible = False

    p = sp.MapPlot(
        projection=Projection.MERCATOR,
        ra_min=17.8,
        ra_max=20.2,
        dec_min=-45.8,
        dec_max=-15.43,
        limiting_magnitude=5.4,
        # hide_colliding_labels=False,
        style=style,
        resolution=1600,
    )
    p.ax.axis("off")
    p.export("temp/constellation-sgr.svg", format="svg", padding=0)
    p.export("temp/constellation-sgr.png", format="png", padding=0)

    p = sp.MapPlot(
        projection=Projection.MERCATOR,
        ra_min=1.75,
        ra_max=3,
        dec_min=19,
        dec_max=28,
        limiting_magnitude=5.4,
        # hide_colliding_labels=False,
        style=style,
        resolution=1600,
    )
    p.ax.axis("off")
    p.export("temp/constellation-ari.svg", format="svg", padding=0)
    p.export("temp/constellation-ari.png", format="png", padding=0)


def create_map_scratch():
    style = PlotStyle().extend(
        # extensions.GRAYSCALE,
        extensions.GRAYSCALE_DARK,
        # extensions.BLUE_LIGHT,
        # extensions.BLUE_MEDIUM,
        # extensions.BLUE_DARK,
        extensions.MAP,
        {
            "star": {"label": {"font_size": 8}, "marker": {"size": 140}},
            "bayer_labels": {
                "font_name": "GFS Didot",
                "font_size": 7,
            },
            "legend": {
                "location": "lower right",
                "num_columns": 1,
                "background_alpha": 1,
            },
        },
    )

    p = sp.MapPlot(
        # projection=Projection.STEREO_NORTH,
        # projection=Projection.STEREO_SOUTH,
        projection=Projection.MERCATOR,
        # Corona Borealis
        ra_min=15,
        ra_max=16.4,
        dec_min=21,
        dec_max=34,
        # ra_min=5.4,
        # ra_max=16,
        # dec_min=23,
        # dec_max=80,
        # ra_min=20,
        # ra_max=24,
        # dec_min=45,
        # dec_max=65,
        limiting_magnitude=14.8,
        limiting_magnitude_labels=0,
        style=style,
        resolution=1800,
        star_catalog="tycho-1",
        # dso_plot_null_magnitudes=False,
        debug=True,
    )

    p.export("temp/map-scratch-1.png", format="png", padding=0.1)


# ------------------------------------------

# create_constellation()

# create_scope_plot_m45()
# create_optic_plot()

# create_scope_view_m45()
# create_scope_view_m11()

# create_zenith()
# create_map_miller()
# create_map_stereo_north()
# create_map_stereo_south()
create_map_orion()
# create_map_scratch()

# create_map_sgr()


print(f"Total run time: {time.time() - start_time}")
