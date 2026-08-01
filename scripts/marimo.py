import marimo

__generated_with = "0.23.16"
app = marimo.App(width="columns")


@app.cell
def scratchpad():
    import time
    from datetime import datetime
    from zoneinfo import ZoneInfo

    from starplot import (
        _,
        MapPlot,
        ZenithPlot,
        HorizonPlot,
        OpticPlot,
        Observer,
        Star,
        DSO,
        Miller,
        callables,
        ObliqueMercator,
        StereoNorth,
        StereoSouth,
        LambertAzEqArea,
        Equidistant,
        geometry,
    )
    from starplot.models.optics import Refractor, Camera
    from starplot.styles import PlotStyle, extensions

    start = time.time()


    style = PlotStyle().extend(
        # extensions.BLUE_MEDIUM,
        extensions.BLUE_NIGHT,
        # extensions.GRAYSCALE,
        extensions.MAP,
        # extensions.FIGURE_TRANSPARENT,
    )

    tz = ZoneInfo("America/Los_Angeles")
    dt = datetime(2024, 10, 19, 21, 00, tzinfo=tz)

    observer = Observer(
        dt=dt,
        lat=32.97,
        lon=-117.038611,
    )
    p = MapPlot(
        projection=Equidistant(
            # center_ra=observer.lst,
            center_dec=90,
        ),
        dec_min=0,
        observer=observer,
        style=style,
        resolution=4000,
        scale=0.7,
        clip_path=geometry.circle(
            center=(0,90),
            diameter_degrees=180,
            num_pts=500,
        )
    )
    p.gridlines(
        labels=False,
        style__label__font_color="black",
        style__label__font_size=60,
    )
    p.constellations()
    p.constellation_borders()

    p.stars(
        where=[_.magnitude < 7], 
        bayer_labels=True,
        flamsteed_labels=True,
        # where_labels=[False]
    )
    p.open_clusters(
        where=[_.magnitude < 12],
        where_labels=[False],
        where_true_size=[False],
    )
    p.galaxies(
        where=[_.magnitude < 12],
        where_labels=[False],
        where_true_size=[False],
    )
    p.nebula(
        where=[_.magnitude < 12],
        where_labels=[False],
        where_true_size=[False],
    )

    p.constellation_labels()
    p.ecliptic()
    p.celestial_equator()
    p.milky_way()


    duration = time.time() - start

    print(duration)

    import marimo
    svg = p.canvas.render()
    marimo.Html(svg)
    return


if __name__ == "__main__":
    app.run()
