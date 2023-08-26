"""
This file is used as a 'scratchpad' during development for testing plots.
"""

import time
from datetime import datetime

from pytz import timezone

from starplot.styles import PlotStyle, BLUE, GRAYSCALE, CHALK, RED, MAP_BLUE, MAP_CHALK
from starplot.models import SkyObject
from starplot.map import Projection

import starplot as sp

start_time = time.time()


def create_map_stereo_vega():
    # style = PlotStyle.load_from_file("blue.yml")
    # style = style.extend({
    #     "bayer_labels": {
    #         "font_name": "GFS Didot",
    #         "font_size": 10
    #     }
    # })
    style = MAP_CHALK
    style = MAP_BLUE
    style.bayer_labels.font_name = "GFS Didot"
    style.bayer_labels.font_size = 10
    p = sp.MapPlot(
        projection=Projection.STEREO_NORTH,
        ra_min=17,
        ra_max=20,
        dec_min=30,
        dec_max=55,
        limiting_magnitude=12.0,
        # style=MAP_BLUE,
        style=style,
        # style=GRAYSCALE,
        # adjust_text=False,
        resolution=4000,
    )
    p.draw_reticle(18.6167, 38.78)
    p.draw_reticle(1.6167, 58.78)
    p.plot_object(
        SkyObject(
            name="M57",
            ra=18.885,
            dec=33.03,
            style={
                "marker": {
                    "size": 10,
                    "symbol": "s",
                    "fill": "full",
                    "color": "red",
                    "alpha": 0.6,
                }
            },
        )
    )
    """
    Vega 
    RA/DEC 18.6167, 38.78
    Correct lon/lat: 81, 38
    Calculated: 99
    """
    p.export("temp/map-stereo-vega.svg", format="svg", padding=0.5)


def create_map_orion():
    style = MAP_BLUE.extend(
        {
            "bayer_labels": {
                "font_name": "GFS Didot",
                "font_size": 6,
                "font_alpha": 0.9,
            },
            # "constellation_borders": {"visible": False},
            # "milky_way": {"visible": False},
        }
    )
    style.star.label.font_size = 8
    # style.star.label.visible = False
    # style.bayer_labels.visible = False

    p = sp.MapPlot(
        projection=Projection.MERCATOR,
        ra_min=3.6,
        ra_max=7.8,
        dec_min=-16,
        dec_max=23.6,
        limiting_magnitude=9.2,
        style=style,
        resolution=4000,
    )
    p.plot_object(
        SkyObject(
            name="M42",
            ra=5.58333,
            dec=-4.61,
            style={
                "marker": {
                    "size": 10,
                    "symbol": "s",
                    "fill": "full",
                    # "color": "#ff6868",
                    "color": "blue",
                    "alpha": 0.7,
                    "zorder": 4096,
                },
                "label": {
                    "font_size": 12,
                    "font_weight": "bold",
                    # "font_color": "blue",
                    "font_color": "darkred",
                    "zorder": 4096,
                },
            },
        )
    )
    p.export("temp/map-orion.svg", format="svg", padding=1)


def create_zenith():
    p = sp.ZenithPlot(
        lat=32.97,
        lon=-117.038611,
        dt=timezone("America/Los_Angeles").localize(datetime.now().replace(hour=21)),
        limiting_magnitude=4.6,
        style=BLUE,
        # style=GRAYSCALE,
        # adjust_text=False,
        include_planets=True,
        resolution=2000,
        include_info_text=True,
    )
    p.plot_object(
        SkyObject(
            name="Mel 111",
            ra=12.36,
            dec=25.85,
            style={
                "marker": {"size": 10, "symbol": "*", "fill": "full", "color": "red"}
            },
        )
    )
    p.export("temp/zenith-poway.svg", format="svg")


def create_map_mercator():
    style = MAP_BLUE.extend(
        {
            "bayer_labels": {
                "font_name": "GFS Didot",
                "font_size": 4,
                "font_alpha": 0.9,
                "visible": False,
            },
            # "constellation_borders": {"visible": False},
            # "milky_way": {"visible": False},
        }
    )
    style.star.label.font_size = 4
    style.constellation.label.font_size = 6
    p = sp.MapPlot(
        projection=Projection.MERCATOR,
        ra_min=0,
        ra_max=24,
        dec_min=-80,
        dec_max=80,
        limiting_magnitude=6,
        style=style,
        resolution=8000,
        adjust_text=False,
    )
    p.export("temp/map-mercator.svg", format="svg")


def create_map_stereo_north():
    p = sp.MapPlot(
        projection=Projection.STEREO_NORTH,
        ra_min=0,
        ra_max=24,
        dec_min=-40,
        dec_max=90,
        limiting_magnitude=8,
        style=CHALK,
        resolution=4000,
        adjust_text=False,
    )
    p.export("temp/temp-map-north.png")


def create_map_stereo_south():
    p = sp.MapPlot(
        projection=Projection.STEREO_SOUTH,
        ra_min=9,
        ra_max=15,
        dec_min=-90,
        dec_max=-40,
        limiting_magnitude=8,
        style=MAP_BLUE,
        resolution=8000,
        adjust_text=False,
    )
    p.export("temp-map-south.svg", format="svg")


def create_map_with_planets():
    style: PlotStyle = MAP_BLUE.extend(
        bayer_labels={"visible": False},
    )
    style.star.label.visible = False
    # style.star.marker.visible = False
    style.constellation.label.visible = False
    style.ecliptic.label.visible = False
    style.celestial_equator.label.visible = False

    # mars pos 8/26/2023: Right Ascension is 11h 57m 08s and the Declination is +01° 03' 38”

    p = sp.MapPlot(
        projection=Projection.MERCATOR,
        ra_min=0,
        ra_max=24,
        dec_min=-70,
        dec_max=70,
        limiting_magnitude=3.2,
        include_planets=True,
        hide_colliding_labels=False,
        style=style,
        resolution=2600,
    )
    p.export("temp/map-planets.svg", format="svg", padding=1)


# ------------------------------------------

create_zenith()
# create_map_mercator()
# create_map_stereo_north()
# create_map_stereo_south()
# create_map_stereo_vega()
# create_map_orion()
create_map_with_planets()

# MAP_BLUE.dump_to_file("blue.yml")

print(f"Total run time: {time.time() - start_time}")
