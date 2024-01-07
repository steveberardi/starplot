from datetime import datetime

from pytz import timezone

from starplot.styles import PlotStyle, extensions
from starplot.models import SkyObject
from starplot.map import Projection

import starplot as sp


"""
    Creates a set of finder charts:

    1. Zenith plot
    2. General area (naked eye, 1x)
    3. Binoculars 10x
    4. Medium power (40x)
    5. Higher power (100x)
"""

sky_object_style = {
    "marker": {
        "size": 15,
        "symbol": "^",
        "fill": "full",
        "color": "#000",
    },
    "label": {
        "font_size": 12,
        "font_weight": "bold",
        # "font_color": "white",
    },
}

sky_objects = [
    SkyObject(
        name="M35",
        ra=6.15,
        dec=24.34,
        style=sky_object_style,
    ),
    SkyObject(
        name="M44",
        ra=8.667,
        dec=19.67,
        style=sky_object_style,
    ),
    # SkyObject(
    #     name="M41",
    #     ra=6.7667,
    #     dec=-20.75,
    #     style=sky_object_style,
    # ),
    # SkyObject(
    #     name="M46",
    #     ra=7.7,
    #     dec=-14.81,
    #     style=sky_object_style,
    # ),
    # SkyObject(
    #     name="M47",
    #     ra=7.6,
    #     dec=-14.48,
    #     style=sky_object_style,
    # ),
    # SkyObject(
    #     name="M93",
    #     ra=7.73,
    #     dec=-23.85,
    #     style=sky_object_style,
    # ),
    # SkyObject(
    #     name="M45",
    #     ra=3.7836111111,
    #     dec=24.1166666667,
    #     style=sky_object_style,
    # ),
]

optics = [
    sp.optics.Binoculars(
        magnification=10,
        fov=65,
    ),
    # sp.optics.Refractor(
    #     focal_length=600,
    #     eyepiece_focal_length=14,
    #     eyepiece_fov=82,
    # ),
    sp.optics.Refractor(
        focal_length=600,
        eyepiece_focal_length=9,
        eyepiece_fov=100,
    ),
]

dt = datetime.now(timezone("America/Los_Angeles")).replace(hour=21, minute=0, second=0)

lat = 32.97
lon = -117.038611


def create_zenith():
    print("Creating whole sky chart...")
    style = PlotStyle().extend(
        extensions.GRAYSCALE,
        extensions.ZENITH,
    )
    style.dso.marker.visible = False
    style.dso.label.visible = False

    p = sp.ZenithPlot(
        lat=lat,
        lon=lon,
        dt=dt,
        limiting_magnitude=4.6,
        style=style,
        resolution=4000,
        hide_colliding_labels=False,
        # include_info_text=True,
        # adjust_text=True,
    )

    for obj in sky_objects:
        p.plot_object(obj)

    p.refresh_legend()
    p.adjust_labels()
    p.export("temp/finder-01-overview.svg", format="svg", padding=0, transparent=True)


def create_map_plots():
    print("Creating map charts...")
    style = PlotStyle().extend(
        # extensions.MINIMAL,
        extensions.GRAYSCALE,
        extensions.MAP,
    )
    style.legend.location = "lower right"
    style.gridlines.line.alpha = 0
    style.milky_way.visible = False
    style.bayer_labels.visible = False

    for i, obj in enumerate(sky_objects):
        mp = sp.MapPlot(
            projection=Projection.MERCATOR,
            ra_min=obj.ra - 2.5,
            ra_max=obj.ra + 2.5,
            dec_min=obj.dec - 20,
            dec_max=obj.dec + 20,
            limiting_magnitude=4.68,
            style=style,
            resolution=2600,
            hide_colliding_labels=False,
        )
        mp.plot_object(obj)
        mp.adjust_labels()

        mp.export(f"temp/finder-02-map-{str(i)}.svg", format="svg", padding=0.3)


def create_optic_plots():
    print("Creating optic charts...")
    style = PlotStyle().extend(
        extensions.MINIMAL,
        extensions.GRAYSCALE,
        extensions.OPTIC,
    )
    style.star.marker.size = 30

    for si, obj in enumerate(sky_objects):
        for oi, optic in enumerate(optics):
            op = sp.OpticPlot(
                ra=obj.ra,
                dec=obj.dec,
                lat=lat,
                lon=lon,
                optic=optic,
                dt=dt,
                limiting_magnitude=12,
                style=style,
                resolution=2000,
                include_info_text=True,
            )
            op.export(
                f"temp/finder-03-optic-{str(si)}-{str(oi)}-{optic.label.lower()}.svg",
                format="svg",
            )


create_zenith()
create_map_plots()
create_optic_plots()
