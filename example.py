import time
from datetime import datetime, timedelta

from pytz import timezone

from starplot.styles import PlotStyle, BLUE, GRAYSCALE, CHALK, RED, MAP_BLUE
from starplot.models import SkyObject
from starplot.map import Projection

import starplot as splt

start_time = time.time()


def create_365():
    for d in range(365):
        dt = datetime(2023, 1, 1) + timedelta(days=d)
        day_of_year = dt.strftime("%j")

        print(f"Day: {day_of_year}")

        create_star_chart(
            lat=32.97,
            lon=-117.038611,
            dt=dt.replace(hour=4, minute=0),
            tz_identifier="UTC",
            filename=f"temp/day-{day_of_year}.png",
            style=BLUE,
            include_info_text=True,
        )


def create_map_stereo_vega():
    # style = PlotStyle.load_from_file("blue.yml")
    # style = style.extend({
    #     "bayer_labels": {
    #         "font_name": "GFS Didot",
    #         "font_size": 10
    #     }
    # })
    style = MAP_BLUE
    style.bayer_labels.font_name = "GFS Didot"
    style.bayer_labels.font_size = 10
    p = splt.MapPlot(
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
    p.export("temp-map-stereo-vega.png")


def create_map_orion():
    style = MAP_BLUE.extend(
        {
            "bayer_labels": {
                "font_name": "GFS Didot",
                "font_size": 9,
                "font_alpha": 0.9,
            },
        }
    )
    style.star.label.font_size = 11

    p = splt.MapPlot(
        projection=Projection.MERCATOR,
        ra_min=3.6,
        ra_max=7.8,
        dec_min=-16,
        dec_max=23.6,
        limiting_magnitude=7.2,
        style=style,
        resolution=1900,
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
                    "color": "#ff6868",
                    "alpha": 1,
                    "zorder": 4096,
                },
                "label": {
                    "font_size": 10,
                    "font_weight": "bold",
                    "font_color": "darkred",
                    "zorder": 4096,
                },
            },
        )
    )
    p.export("temp-orion.png")


def create_zenith():
    p = splt.ZenithPlot(
        lat=32.97,
        lon=-117.038611,
        dt=timezone("America/Los_Angeles").localize(datetime.now().replace(hour=21)),
        limiting_magnitude=4.6,
        style=BLUE,
        # style=GRAYSCALE,
        # adjust_text=False,
        resolution=2000,
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
    p.export("temp-zenith-new.png", format="png")


def create_map_mercator():
    p = splt.MapPlot(
        projection=Projection.MERCATOR,
        ra_min=0,
        ra_max=24,
        dec_min=-80,
        dec_max=80,
        limiting_magnitude=6,
        style=MAP_BLUE,
        resolution=4000,
        adjust_text=False,
    )
    p.export("temp-map-mercator.png")


def create_map_stereo_north():
    p = splt.MapPlot(
        projection=Projection.STEREO_NORTH,
        ra_min=0,
        ra_max=24,
        dec_min=0,
        dec_max=90,
        limiting_magnitude=12,
        style=MAP_BLUE,
        resolution=8000,
        adjust_text=False,
    )
    p.export("temp-map-north.png")


# create_style_examples()
# create_365()
# create_example()
# create_map_orion()
# create_map_all()

# create_zenith()
# create_map_mercator()
# create_map_stereo_north()
# create_map_stereo_vega()
create_map_orion()

# MAP_BLUE.dump_to_file("blue.yml")

print(f"Total run time: {time.time() - start_time}")
