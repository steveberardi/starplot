import time
from datetime import datetime, timedelta

from pytz import timezone

from starplot.styles import BLUE, GRAYSCALE, CHALK, RED, MAP_BLUE
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


def create_map_vega():
    p = splt.MapPlot(
        projection=Projection.STEREO_NORTH,
        # projection=Projection.MERCATOR,
        ra_min=15,
        ra_max=19,
        dec_min=30,
        dec_max=65,
        limiting_magnitude=9.0,
        style=MAP_BLUE,
        # style=GRAYSCALE,
        adjust_text=False,
        resolution=4000,
    )
    p.draw_reticle(18.6167, 38.78)
    p.draw_reticle(1.6167, 58.78)
    p.plot_object(
        SkyObject(
            name="M57",
            ra=18.885,  # 283.275,  # 18.885,
            dec=33.03,
            style={
                "marker": {
                    "size": 10,
                    "symbol": "s",
                    "fill": "full",
                    "color": "red",
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
    p.export("temp-vega.png")


def create_map_all():
    splt = MapPlot(
        projection=Projection.MERCATOR,
        ra_min=0,
        ra_max=24,
        dec_min=-90,
        dec_max=90,
        limiting_magnitude=8.0,
        style=MAP_BLUE,
        adjust_text=False,
        resolution=8000,
        # style=GRAYSCALE,
    )
    splt.draw_reticle(279.2499984, 38.78)
    splt.plot_object(
        SkyObject(
            name="M57",
            ra=283.275,  # 18.885,
            dec=33.03,
            style={
                "marker": {
                    "size": 10,
                    "symbol": "s",
                    "fill": "full",
                    "color": "red",
                }
            },
        )
    )
    splt.export("temp-all.png")

def create_map_orion():
    p = splt.MapPlot(
        # projection=Projection.STEREO_NORTH,
        projection=Projection.MERCATOR,
        ra_min=3.5,
        ra_max=8.8,
        dec_min=-16,
        dec_max=24,
        limiting_magnitude=7.2,
        style=MAP_BLUE,
        resolution=4000,
    )
    p.plot_object(
        SkyObject(
            name="M42",
            ra=5.58333,
            dec=-4.61,
            style={
                "marker": {
                    "size": 12,
                    "symbol": "s",
                    "fill": "full",
                    "color": "#ff6868",
                    "alpha": 0.76,
                },
                "label": {
                    "font_size": 12,
                    "font_weight": "bold",
                    "font_color": "darkred"
                }
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
        adjust_text=False,
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
    p.export("temp-zenith-new.svg", format="svg")

def create_map():
    p = splt.MercatorPlot(
        # projection=Projection.STEREO_NORTH,
        projection=Projection.MERCATOR,
        ra_min=0,
        ra_max=24,
        dec_min=-80,
        dec_max=80,
        limiting_magnitude=6,
        style=MAP_BLUE,
        resolution=12000,
    )
    p.export("temp-map.png")

# create_style_examples()
# create_365()
# create_example()
# create_map_orion()
# create_zenith()
# create_map_all()
create_map()

print(f"Total run time: {time.time() - start_time}")
