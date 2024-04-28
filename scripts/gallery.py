from datetime import datetime
from pytz import timezone
from starplot import MapPlot, Projection, callables, DSO, Star
from starplot.data import constellations
from starplot.styles import PlotStyle, extensions

import starplot as sp

IMAGE_PATH = "docs/images/gallery/"

RESOLUTION = 2800

bayer_labels = {
    "bayer_labels": {
        "font_name": "GFS Didot",
        "font_size": 7,
    }
}


def zenith():
    print("Creating Zenith...")
    ext = [
        extensions.BLUE_MEDIUM,
        extensions.NORD,
    ]
    for i, e in enumerate(ext):
        tz = timezone("America/Los_Angeles")
        dt = datetime(2023, 7, 13, 22, 0, tzinfo=tz)  # July 13, 2023 at 10pm PT
        p = MapPlot(
            projection=Projection.ZENITH,
            lat=33.363484,
            lon=-116.836394,
            dt=dt,
            style=PlotStyle().extend(
                e,
                extensions.ZENITH,
            ),
            resolution=RESOLUTION,
        )
        p.constellations()
        p.stars(mag=5.6, where_labels=[Star.magnitude < 2.1])
        p.dsos(mag=9, true_size=True, labels=None)

        # p.constellation_borders()
        if i in [0]:
            p.gridlines(labels=False)
            p.ecliptic()
            p.celestial_equator()
            p.milky_way()

        p.export(IMAGE_PATH + f"zenith_{i}.png", transparent=True)


def orion():
    print("Creating Orion...")
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
    p = MapPlot(
        projection=Projection.MERCATOR,
        ra_min=3.4,
        ra_max=8,
        dec_min=-20,
        dec_max=28,
        style=style,
        resolution=RESOLUTION,
    )
    p.constellations()
    p.stars(mag=10, bayer_labels=True)
    p.dsos(mag=10, true_size=True, labels=None)
    p.constellation_borders()
    p.ecliptic()
    p.celestial_equator()
    p.milky_way()
    p.gridlines()
    p.legend()
    p.export(IMAGE_PATH + "orion.png", padding=0.2)


def lmc():
    print("Creating Large Magellanic Cloud...")
    style = PlotStyle().extend(
        # extensions.GRAYSCALE,
        # extensions.GRAYSCALE_DARK,
        # extensions.BLUE_LIGHT,
        # extensions.BLUE_MEDIUM,
        extensions.BLUE_DARK,
        extensions.MAP,
        {
            "star": {
                "label": {"font_size": 8},
                "marker": {"size": 30},
            },
            "bayer_labels": {
                "font_name": "GFS Didot",
                "font_size": 9,
            },
            "legend": {
                "location": "lower right",
                "num_columns": 1,
                "background_alpha": 1,
            },
            # "dso_galaxy": {
            #     "marker": {
            #         "color": "#fa87c0",
            #         "alpha": 0.2,
            #         "zorder": -200,
            #     }
            # },
        },
    )
    p = MapPlot(
        projection=Projection.STEREO_SOUTH,
        ra_min=4,
        ra_max=6.5,
        dec_min=-76,
        dec_max=-63,
        style=style,
        resolution=RESOLUTION,
    )
    p.constellations()
    p.stars(mag=13)
    p.galaxies(mag=12, labels=None)
    p.nebula(mag=12, labels=None)
    p.open_clusters(mag=12, true_size=False, labels=None)
    p.globular_clusters(mag=12, true_size=False, labels=None)
    p.constellation_borders()
    p.ecliptic()
    p.celestial_equator()
    p.milky_way()
    p.gridlines()
    p.legend()
    p.export(IMAGE_PATH + "magellanic_cloud.png", padding=0.2)


def sgr():
    print("Creating Sagittarius...")
    style = PlotStyle().extend(
        extensions.BLUE_LIGHT,
        # extensions.BLUE_MEDIUM,
        extensions.MAP,
        bayer_labels,
    )
    p = MapPlot(
        projection=Projection.STEREO_SOUTH,
        ra_min=17,
        ra_max=19.5,
        dec_min=-46,
        dec_max=-14,
        style=style,
        resolution=RESOLUTION,
    )
    p.constellations()
    p.stars(mag=13, bayer_labels=True)
    p.dsos(mag=13, true_size=True, labels=None)
    p.constellation_borders()
    p.ecliptic()
    p.celestial_equator()
    p.milky_way()
    p.gridlines()
    p.export(IMAGE_PATH + "sagittarius.png", padding=0.2)


def optics():
    print("Creating Optics...")
    style = PlotStyle().extend(
        # extensions.MINIMAL,
        extensions.GRAYSCALE_DARK,
        # extensions.GRAYSCALE,
        # extensions.BLUE_LIGHT,
        extensions.OPTIC,
    )

    dt = datetime.now(timezone("America/Los_Angeles")).replace(
        year=2024, month=2, day=4, hour=21, minute=0, second=0
    )

    p1 = sp.OpticPlot(
        # Orion Nebula
        ra=5.583,
        dec=-5.383,
        lat=32.97,
        lon=-117.038611,
        # TV-85
        optic=sp.optics.Refractor(
            focal_length=600,
            eyepiece_focal_length=11,
            eyepiece_fov=100,
        ),
        dt=dt,
        style=style,
        resolution=RESOLUTION,
    )
    p1.stars(mag=15, color_fn=callables.color_by_bv, bayer_labels=True)
    p1.dsos(mag=4.1, labels=None)
    p1.info()

    p2 = sp.OpticPlot(
        # M45
        ra=3.7836111111,
        dec=24.1166666667,
        lat=32.97,
        lon=-117.038611,
        # AT72EDII
        optic=sp.optics.Refractor(
            focal_length=430,
            eyepiece_focal_length=11,
            eyepiece_fov=82,
        ),
        dt=dt,
        style=style,
        resolution=RESOLUTION,
    )
    p2.stars(mag=15, color_fn=callables.color_by_bv, bayer_labels=True)
    p2.info()

    p3 = sp.OpticPlot(
        # M44
        ra=8.667,
        dec=19.67,
        lat=32.97,
        lon=-117.038611,
        # 10x binoculars
        optic=sp.optics.Binoculars(
            magnification=10,
            fov=65,
        ),
        dt=dt,
        style=style.extend({"star": {"marker": {"size": 64}}}),
        resolution=RESOLUTION,
    )
    p3.stars(mag=11, color_fn=callables.color_by_bv, bayer_labels=True)
    p3.info()

    p1.export(IMAGE_PATH + "optic_01.png", padding=0.3)
    p2.export(IMAGE_PATH + "optic_02.png", padding=0.3)
    p3.export(IMAGE_PATH + "optic_03.png", padding=0.3)


def orthographic():
    print("Creating Orthographic...")
    ext = [
        extensions.BLUE_MEDIUM,
        extensions.GRAYSCALE_DARK,
    ]
    for i, e in enumerate(ext):
        style = PlotStyle().extend(
            e,
            extensions.MAP,
        )

        tz = timezone("America/Los_Angeles")
        dt = datetime(2024, 10, 19, 21, 00, tzinfo=tz)

        p = MapPlot(
            projection=Projection.ORTHOGRAPHIC,
            lat=32.97,
            lon=-117.038611,
            dt=dt,
            ra_min=0,
            ra_max=24,
            dec_min=-90,
            dec_max=90,
            style=style,
            resolution=RESOLUTION,
        )
        p.gridlines(labels=False)
        p.stars(mag=7.86, where_labels=[Star.magnitude < 6])
        p.open_clusters(mag=8, true_size=False, labels=None)
        p.galaxies(mag=8, true_size=False, labels=None)
        p.nebula(mag=8, true_size=True, labels=None)
        p.constellations(
            labels=constellations.CONSTELLATIONS_FULL_NAMES,
            style={"label": {"font_size": 9, "font_alpha": 0.8}},
        )
        p.constellation_borders()
        p.ecliptic()
        p.celestial_equator()
        p.milky_way()
        p.planets()
        p.adjust_text()

        p.export(IMAGE_PATH + f"orthographic_0{i+1}.png", padding=0.3)


def miller_big():
    print("Creating Big Miller...")
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
        resolution=6000,
    )
    p.stars(mag=8)
    p.dsos(
        labels=None,
        where=[
            DSO.magnitude <= 8,
            DSO.size > 0.05,
        ],
    )
    p.gridlines()
    p.milky_way()
    p.ecliptic(style={"line": {"style": "dashed"}})
    p.celestial_equator()

    p.export(IMAGE_PATH + "miller_big.png", padding=0.5)


def antique():
    print("Creating Antique...")
    style = PlotStyle().extend(
        extensions.ANTIQUE,
        extensions.MAP,
        bayer_labels,
    )
    p = MapPlot(
        projection=Projection.STEREO_NORTH,
        ra_min=1,
        ra_max=6,
        dec_min=20,
        dec_max=70,
        style=style,
        resolution=RESOLUTION,
    )
    p.gridlines(labels=False)
    p.stars(mag=9.4, style={"marker": {"size": 20}})
    p.stars(mag=8, bayer_labels=True, style={"marker": {"alpha": 0}})
    p.stars(
        mag=2.3,
        style={
            "marker": {
                "size": 54,
                "symbol": "star_8",
                "zorder": 50,
            }
        },
        legend_label=None,
        labels=None,
    )
    p.constellations()
    p.constellation_borders()
    p.dsos(mag=12, labels=None)
    p.milky_way()
    p.export(IMAGE_PATH + "antique.png", padding=0.5)


antique()
zenith()
orion()
sgr()
lmc()
optics()
orthographic()
miller_big()

# functions = [
#     zenith,
#     orion,
# ]

# for i, func in enumerate(functions):
#     func(f"{i+1:03}.png")
