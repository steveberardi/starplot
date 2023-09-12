"""
This file is used as a 'scratchpad' during development for testing plots.
"""

import time
from datetime import datetime

from pytz import timezone

from starplot.styles import PlotStyle, extensions
from starplot.models import SkyObject
from starplot.map import Projection

import starplot as sp

start_time = time.time()


def create_map_orion():
    style = PlotStyle().extend(
        extensions.GRAYSCALE,
        # extensions.BLUE_LIGHT,
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
        },
    )

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
    # marker for M42
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
                    # "font_name": "GFS Didot",
                    "font_color": "darkred",
                    "zorder": 4096,
                },
            },
        )
    )
    p.export("temp/map-orion.svg", format="svg", padding=1)


def create_zenith():
    """Create zenith plot for tonight's sky in Poway"""
    style = PlotStyle().extend(
        extensions.GRAYSCALE,
        # extensions.BLUE_LIGHT,
        # extensions.BLUE_MEDIUM,
        # extensions.BLUE_DARK,
        extensions.ZENITH,
    )
    p = sp.ZenithPlot(
        lat=32.97,
        lon=-117.038611,
        dt=datetime.now(timezone("America/Los_Angeles")).replace(hour=21),
        limiting_magnitude=4.6,
        # style=sp.styles.ZENITH_BLUE_MEDIUM,
        # style=style,
        include_planets=True,
        resolution=2000,
        include_info_text=True,
        adjust_text=True,
    )
    p.export("temp/zenith-poway.svg", format="svg")


def create_map_mercator():
    """Create near full extent of map with mercator projection"""
    style = sp.styles.MAP_BLUE_DARK.extend(
        sp.styles.extensions.HIDE_LABELS,
        {
            "bayer_labels": {
                "font_name": "GFS Didot",
                "font_size": 4,
                "font_alpha": 0.9,
                "visible": False,
            },
            "constellation_borders": {"visible": False},
        },
    )
    style.star.label.font_size = 4
    style.constellation.label.font_size = 6
    style.constellation.line.width = 2
    p = sp.MapPlot(
        projection=Projection.MERCATOR,
        ra_min=0,
        ra_max=24,
        dec_min=-70,
        dec_max=70,
        limiting_magnitude=6,
        style=style,
        resolution=8000,
        adjust_text=False,
    )
    p.export("temp/map-mercator.svg", format="svg", padding=0.5)


def create_map_stereo_north():
    p = sp.MapPlot(
        projection=Projection.STEREO_NORTH,
        ra_min=0,
        ra_max=24,
        dec_min=10,
        dec_max=90,
        limiting_magnitude=6,
        style=sp.styles.MAP_BLUE_DARK.extend(sp.styles.extensions.HIDE_LABELS),
        resolution=4000,
    )
    p.export("temp/temp-map-north.svg", format="svg", padding=0.5)


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


def create_map_with_planets():
    style: PlotStyle = sp.styles.MAP_BLUE_LIGHT.extend(
        bayer_labels={"visible": False},
    )
    style.star.label.visible = False
    # style.star.marker.visible = False
    style.constellation.label.visible = False
    style.ecliptic.label.visible = False
    style.celestial_equator.label.visible = False

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


def create_map_sgr():
    style = PlotStyle().extend(
        # sp.styles.extensions.HIDE_LABELS,
        extensions.GRAYSCALE,
        # extensions.BLUE_LIGHT,
        # extensions.BLUE_MEDIUM,
        # extensions.BLUE_DARK,
        extensions.MAP,
        {
            "bayer_labels": {
                "font_name": "GFS Didot",
                "font_size": 8,
            },
            # "constellation_borders": {"visible": False},
            # milky_way={"visible": False},
        },
    )
    # style.star.label.visible = False
    # style.star.marker.visible = False
    # style.constellation.label.visible = False
    # style.ecliptic.label.visible = False
    # style.celestial_equator.label.visible = False
    # style.gridlines.label.font_size = 8

    p = sp.MapPlot(
        projection=Projection.STEREO_SOUTH,
        # SGR
        ra_min=16,
        ra_max=20,
        dec_min=-50,
        dec_max=-10,
        # CYG
        # ra_min=19,
        # ra_max=21,
        # dec_min=35,
        # dec_max=55,
        limiting_magnitude=6,
        # include_planets=True,
        # hide_colliding_labels=False,
        style=style,
        resolution=2000,
    )
    p.export("temp/map-sgr.svg", format="svg", padding=0.3)
    # p.export("temp/map-sgr.png", format="png", padding=0.3)


def create_galaxy_test():
    style = PlotStyle().extend(
        # sp.styles.extensions.HIDE_LABELS,
        # extensions.GRAYSCALE,
        # extensions.BLUE_LIGHT,
        # extensions.BLUE_MEDIUM,
        extensions.BLUE_DARK,
        extensions.MAP,
        {
            "bayer_labels": {
                "font_name": "GFS Didot",
                "font_size": 8,
            },
        },
    )
    p = sp.MapPlot(
        projection=Projection.MERCATOR,
        ra_min=11,
        ra_max=16,
        dec_min=-5,
        dec_max=40,
        limiting_magnitude=9,
        # include_planets=True,
        # hide_colliding_labels=False,
        style=style,
        resolution=2000,
    )
    p.export("temp/galaxy.svg", format="svg", padding=0.3)


def dump_extensions():
    import yaml

    ext = {
        "blue_light": extensions.BLUE_LIGHT,
        "blue_medium": extensions.BLUE_MEDIUM,
        "blue_dark": extensions.BLUE_DARK,
        "grayscale": extensions.GRAYSCALE,
        "map": extensions.MAP,
        "zenith": extensions.ZENITH,
    }

    for k, v in ext.items():
        with open(f"temp/{k}.yml", "w") as outfile:
            style_yaml = yaml.dump(v)
            outfile.write(style_yaml)


# ------------------------------------------

create_galaxy_test()

create_zenith()
# create_map_mercator()
# create_map_stereo_north()
# create_map_stereo_south()
create_map_orion()
create_map_sgr()

# create_map_with_planets()

# dump_extensions()

print(f"Total run time: {time.time() - start_time}")
