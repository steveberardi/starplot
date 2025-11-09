from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from starplot import OpticPlot, Observer, Satellite, Moon, Binoculars, _
from starplot.styles import PlotStyle, extensions

tz = ZoneInfo("US/Pacific")
dt = datetime(2025, 12, 8, 8, 3, 16, tzinfo=tz)

style = PlotStyle().extend(
    extensions.BLUE_NIGHT,
    extensions.OPTIC,
    extensions.GRADIENT_DAYLIGHT,
)

observer = Observer(
    dt=dt,
    lat=33.0225027778,
    lon=-116.507025,
)

moon = Moon.get(dt=observer.dt, lat=observer.lat, lon=observer.lon)

p = OpticPlot(
    ra=moon.ra,
    dec=moon.dec,
    observer=observer,
    optic=Binoculars(
        magnification=15,
        fov=65,
    ),
    style=style,
    resolution=2400,
    autoscale=True,
)
p.moon(true_size=True, show_phase=True, label=None)

iss = Satellite.from_tle(
    name="ISS (ZARYA)",
    line1="1 25544U 98067A   25312.42041502  .00013418  00000+0  24734-3 0  9990",
    line2="2 25544  51.6332 312.3676 0004093  47.8963 312.2373 15.49452868537539",
    lat=observer.lat,
    lon=observer.lon,
)

dt_start = observer.dt - timedelta(minutes=1)
dt_end = observer.dt + timedelta(minutes=1)

for sat in iss.trajectory(dt_start, dt_end, step=timedelta(seconds=1)):
    if sat.geometry.intersects(moon.geometry):
        marker_color = "red"
        label_color = "#ffcccc"
    else:
        marker_color = "gold"
        label_color = "#c7e5ff"

    p.marker(
        sat.ra,
        sat.dec,
        style={
            "marker": {
                "size": 60,
                "edge_width": 2,
                "symbol": "plus",
                "color": marker_color,
                "zorder": 5_000,
            },
            "label": {
                "font_color": label_color,
                "border_color": "#000",
                "border_width": 6,
                "font_size": 38,
                "font_weight": "heavy",
                "offset_x": "auto",
                "offset_y": "auto",
                "zorder": 5_000,
            },
        },
        label=sat.dt.strftime("%-H:%M:%S"),
    )

p.export("optic_iss_transit.png", padding=0.1, transparent=True)
