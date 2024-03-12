"""
This file is used as a 'scratchpad' during development for testing plots.
"""

import time
from datetime import datetime

from pytz import timezone

from starplot.styles import PlotStyle, extensions, PolygonStyle
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
        # extensions.BLUE_LIGHT,
        # extensions.BLUE_MEDIUM,
        # extensions.BLUE_DARK,
        extensions.MAP,
        extensions.ANTIQUE,
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
                "num_columns": 8,
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
        style=style,
        resolution=3200,
        debug=True,
    )

    p.stars(
        mag=2.3,
        style={
            "marker": {
                "size": 46,
                "symbol": "star_8",
                "zorder": 50,
            }
        },
        legend_label=None,
        labels=None,
    )
    p.stars(
        # catalog="tycho-1",
        mag=10,
        bayer_labels=True,
        labels=None,
    )
    p.dsos(
        mag=12,
        null=True,
        # labels={"NGC2260": "2260www"},
        labels=None,
        legend_labels={sp.data.dsos.DsoType.OPEN_CLUSTER: None}
        # names=["NGC1976", "Mel022", "C041"],
    )

    p.constellations()
    p.constellation_borders()
    p.milky_way()
    p.ecliptic(label=None)
    p.title("Orion in Mercator")

    # p.marker(
    #     ra=4.5,
    #     dec=5,
    #     label="hello",
    #     style={
    #         "marker": {
    #             "size": 10,
    #             "symbol": "circle_plus",
    #             "color": "black",
    #             "edge_color": "black",
    #             "alpha": 0.7,
    #             "zorder": 4096,
    #         },
    #         "label": {
    #             "font_size": 12,
    #             "font_weight": "bold",
    #             # "font_color": "blue",
    #             # "font_name": "GFS Didot",
    #             "font_color": "darkred",
    #             "zorder": 4096,
    #         },
    #     },
    #     legend_label="crossmarker",
    # )

    points = [
        (5, 10),
        (6, 10),
        (6, 0),
        (5, 0),
        (5, 10),
    ]

    # p.polygon(
    #     points,
    #     pstyle,
    # )

    # p.bino_fov(ra=5.6, dec=-1.2, fov=65, magnification=10)

    p.gridlines(tick_marks=True)
    p.legend()

    # p.export("temp/map-orion.svg", format="svg", padding=1)
    p.export("temp/map-orion.png", padding=0.5)


def create_zenith():
    """Create zenith plot for tonight's sky in Poway"""
    style = PlotStyle().extend(
        # extensions.GRAYSCALE,
        # extensions.GRAYSCALE_DARK,
        # extensions.BLUE_LIGHT,
        # extensions.BLUE_MEDIUM,
        # extensions.ANTIQUE,
        extensions.BLUE_DARK,
        extensions.ZENITH,
    )
    p = sp.MapPlot(
        projection=Projection.ZENITH,
        lat=32.97,
        lon=-117.038611,
        dt=datetime.now(timezone("America/Los_Angeles")).replace(hour=21),
        style=style,
        resolution=2400,
    )
    p.stars(mag=4.6)
    p.constellations()
    p.constellation_borders()
    p.ecliptic()
    p.celestial_equator()
    # p.legend()
    p.milky_way()
    p.info()
    p.export("temp/zenith-poway.png", format="png", transparent=True, padding=0.4)


def create_map_miller():
    """Create near full extent of map with miller projection"""
    style = PlotStyle().extend(
        # extensions.GRAYSCALE,
        # extensions.GRAYSCALE_DARK,
        # extensions.BLUE_LIGHT,
        # extensions.BLUE_MEDIUM,
        extensions.BLUE_DARK,
        # extensions.ANTIQUE,
        extensions.MAP,
    )

    style.star.label.font_size = 4
    style.constellation.label.font_size = 6
    style.constellation.line.width = 2

    p = sp.MapPlot(
        projection=Projection.MILLER,
        ra_min=0,
        ra_max=24,
        dec_min=-80,
        dec_max=80,
        style=style,
        resolution=8000,
        debug=True,
    )
    p.stars(mag=8, labels=None)
    p.dsos(mag=8, null=True, labels=None)
    p.gridlines()
    p.milky_way()
    p.planets()
    p.ecliptic(style={"line": {"style": "dashed"}})
    p.celestial_equator()
    p.export("temp/map-miller.png", padding=0.5)


def create_optic_plot():
    style = PlotStyle().extend(
        # extensions.GRAYSCALE_DARK,
        # extensions.GRAYSCALE,
        # extensions.BLUE_LIGHT,
        extensions.BLUE_DARK,
        extensions.OPTIC,
    )

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
        ra=5.6,
        dec=-1.2,
        # Orion Nebula
        # ra=5.583,
        # dec=-5.383,
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
        #     eyepiece_focal_length=11,
        #     eyepiece_fov=100,
        # ),
        dt=datetime.now(timezone("America/Los_Angeles")).replace(
            hour=20, minute=30, second=0
        ),
        style=style,
        resolution=1800,
        debug=True,
    )
    p1.celestial_equator()
    p1.ecliptic()
    p1.stars(mag=15, color_fn=callables.color_by_bv)
    p1.dsos(mag=4.1, labels=None)
    p1.title("Orion Nebula")

    p2 = sp.OpticPlot(
        # M45
        # ra=3.7836111111,
        # dec=24.1166666667,
        # double cluster
        # ra=2.33,
        # dec=57.14,
        ra=6.1,
        dec=22,
        # M44
        # ra=8.667,
        # dec=19.67,
        # Hyades
        # ra=4.501,
        # dec=15.96,
        lat=32.97,
        lon=-117.038611,
        # 10x binoculars
        optic=sp.optics.Binoculars(
            magnification=10,
            fov=65,
        ),
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
        style=style,
        resolution=1600,
        debug=True,
    )
    p2.ecliptic()
    p2.stars(mag=10, bayer_labels=True)
    p2.info()

    # p1.export("temp/optic-p1.svg", format="svg", padding=0.3)
    # p2.export("temp/optic-p2.svg", format="svg", padding=0.3)

    p1.export("temp/optic-p1.png", padding=0.3)
    p2.export("temp/optic-p2.png", padding=0.3)


def create_map_scratch():
    style = PlotStyle().extend(
        # extensions.GRAYSCALE,
        # extensions.GRAYSCALE_DARK,
        # extensions.BLUE_LIGHT,
        # extensions.ANTIQUE,
        # extensions.BLUE_MEDIUM,
        extensions.BLUE_DARK,
        extensions.MAP,
        {
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
        projection=Projection.ORTHOGRAPHIC,
        # Corona Borealis
        # ra_min=15,
        # ra_max=16.4,
        # dec_min=21,
        # dec_max=34,
        # ra_min=5.4,
        # ra_max=16,
        # dec_min=23,
        # dec_max=80,
        # ra_min=20,
        # ra_max=24,
        # dec_min=45,
        # dec_max=65,
        lat=32.97,
        lon=-117.038611,
        dt=datetime.now(timezone("America/Los_Angeles")).replace(hour=21),
        style=style,
        resolution=3200,
        debug=True,
    )
    p.stars(mag=5.6)  # , catalog="tycho-1")
    p.dsos(mag=9, true_size=True)
    p.constellations()
    p.constellation_borders()
    p.gridlines(labels=False)
    p.milky_way()
    p.adjust_text()

    p.export("temp/map-scratch-1.png", format="png", padding=0.5)


# ------------------------------------------

# create_optic_plot()

# create_zenith()

create_map_miller()

create_map_orion()

# create_map_scratch()

print(f"Total run time: {time.time() - start_time}")
