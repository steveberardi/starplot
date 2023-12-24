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
        "size": 16,
        "symbol": "D",
        "fill": "full",
        "color": "#000",
    },
    "label": {
        "font_size": 12,
        "font_weight": "bold",
        "font_color": "black",
    },
}

sky_objects = [
    # SkyObject(
    #     name="M35",
    #     ra=6.15,
    #     dec=24.34,
    #     style=sky_object_style,
    # ),
    SkyObject(
        name="M45",
        ra=3.7836111111,
        dec=24.1166666667,
        style=sky_object_style,
    ),
]

optics = [
    sp.optic.Binoculars(
        magnification=10,
        fov=65,
    ),
    sp.optic.Refractor(
        focal_length=600,
        eyepiece_focal_length=14,
        eyepiece_fov=82,
    ),
    sp.optic.Refractor(
        focal_length=600,
        eyepiece_focal_length=7,
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
    p = sp.ZenithPlot(
        lat=lat,
        lon=lon,
        dt=dt,
        limiting_magnitude=4.6,
        style=style,
        resolution=4000,
        include_info_text=True,
        adjust_text=True,
    )

    for obj in sky_objects:
        p.plot_object(obj)

    p.refresh_legend()
    p.export("temp/finder-01-overview.png", format="png", transparent=True)


def create_map_plot():
    print("Creating map chart...")
    style = PlotStyle().extend(
        # extensions.MINIMAL,
        extensions.GRAYSCALE,
        extensions.MAP,
    )

    for obj in sky_objects:
        mp = sp.MapPlot(
            projection=Projection.MERCATOR,
            ra_min=obj.ra - 2,
            ra_max=obj.ra + 2,
            dec_min=obj.dec - 15,
            dec_max=obj.dec + 15,
            limiting_magnitude=7.2,
            style=style,
            resolution=2600,
        )
        mp.plot_object(obj)

        mp.export(f"temp/finder-02-map.png", padding=0.3)


def create_optic_plots():
    print("Creating optic charts...")
    style = PlotStyle().extend(
        extensions.MINIMAL,
        extensions.GRAYSCALE,
        extensions.OPTIC,
    )

    for obj in sky_objects:
        for i, optic in enumerate(optics):
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
            op.export(f"temp/finder-03-optic-{str(i)}-{optic.label.lower()}.png")


create_zenith()
create_map_plot()
create_optic_plots()
