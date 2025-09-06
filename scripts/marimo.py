import marimo

__generated_with = "0.15.2"
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
    )
    from starplot.optics import Refractor, Camera
    from starplot.styles import PlotStyle, extensions

    start = time.time()

    tz = ZoneInfo("America/Los_Angeles")
    dt = datetime(2023, 7, 13, 22, 0, tzinfo=tz)  # July 13, 2023 at 10pm PT

    observer = Observer(
        lat=33.363484,
        lon=-116.836394,
        dt=dt,
    )

    p = ZenithPlot(
        observer=observer,
        style=PlotStyle().extend(
            extensions.BLUE_GOLD,
            extensions.GRADIENT_BOLD_SUNSET,
        ),
        resolution=3600,
        autoscale=True,
        debug=True,
    )
    p.horizon()
    p.constellations()
    p.stars(where=[_.magnitude < 4.6], where_labels=[_.magnitude < 2.1])

    p.galaxies(where=[_.magnitude < 9], true_size=False, labels=None)
    p.open_clusters(where=[_.magnitude < 9], true_size=False, labels=None)

    p.constellation_borders()
    p.ecliptic()
    p.celestial_equator()
    p.milky_way()
    p.constellation_labels()

    duration = time.time() - start

    print(duration)

    p.fig.gca()

    return


if __name__ == "__main__":
    app.run()
