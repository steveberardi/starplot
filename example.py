import time
from datetime import datetime, timedelta

from starplot.charts import create_star_chart
from starplot.styles import BLUE, GRAYSCALE, CHALK, RED, MAP_BLUE
from starplot.models import SkyObject
from starplot.plot import StarPlot, Projection, MapPlot

start_time = time.time()


def create_example():
    extra = [
        SkyObject(
            name="Mel 111",
            ra=12.36,
            dec=25.85,
            style={
                "marker": {"size": 10, "symbol": "*", "fill": "full", "color": "red"}
            },
        ),
    ]

    create_star_chart(
        lat=32.97,
        lon=-117.038611,
        dt=datetime.now().replace(hour=21, minute=0, second=0),
        # dt=datetime(2023, 12, 28).replace(hour=22),
        # dt=datetime(1983, 6, 8),
        tz_identifier="America/Los_Angeles",
        filename="temp-tonight.png",
        style=GRAYSCALE,
        # extra_objects=extra,
        include_info_text=True,
    )


def create_style_examples():
    styles = {
        "blue": BLUE,
        "grayscale": GRAYSCALE,
        "chalk": CHALK,
        "red": RED,
    }
    for name, style in styles.items():
        create_star_chart(
            lat=32.97,
            lon=-117.038611,
            dt=datetime.now().replace(hour=22),
            # dt=datetime(2023, 12, 28).replace(hour=22),
            # dt=datetime(2023, 2, 8),
            tz_identifier="America/Los_Angeles",
            filename=f"examples/starchart-{name}.png",
            style=style,
        )


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


def create_map():
    splt = MapPlot(
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
    splt.draw_reticle(18.6167, 38.78)
    splt.draw_reticle(1.6167, 58.78)
    splt.plot_object(
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
    splt.export("temp-vega.png")


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


# create_style_examples()
# create_365()
create_example()
create_map()
# create_map_all()

print(f"Total run time: {time.time() - start_time}")
