from datetime import datetime
from zoneinfo import ZoneInfo

from starplot import Observer, HorizonPlot, styles, callables, DSO, _

tz = ZoneInfo("America/Los_Angeles")
dt = datetime(2025, 11, 18, 21, 30, 0, tzinfo=tz)

observer = Observer(
    dt=dt,
    lat=32.97,
    lon=-117.038611,
)

style = styles.PlotStyle().extend(
    styles.extensions.GRAYSCALE_DARK,
    styles.extensions.HORIZON,
)
style.axes.background.fill = {
    "stops": styles.gradients.NIGHT,
    "type": "linear",
}
style.figure.background.fill = "#000"

p = HorizonPlot(
    altitude=(0, 70),
    azimuth=(30, 150),
    observer=observer,
    style=style,
    resolution=2000,
    autoscale=True,
)
p.ground(min_altitude=5, max_altitude=8)
p.stars(
    where=[_.magnitude < 3.6],
    where_labels=[_.magnitude < 1.6],
    # callable to color the stars based on their BV index:
    color_fn=callables.color_by_bv_gradient,
    # callable to make dimmer stars semi-transparent:
    opacity_fn=lambda s: 1 if s.magnitude < 2 else 0.5,
)

style.gridlines.label.font_size *= 1.2  # make the labels 20% bigger
style.gridlines.label.fill = "#e5ecf3"
style.gridlines.line.width = 0  # hide the gridlines, we just want the labels
p.gridlines(alt_label_locations=[])

# Plot a dotted circle around the Pleiades (M45) and an arrow pointing to it
m45 = DSO.get(m="45")
p.polygon(
    geometry=m45.geometry,
    style={
        "fill": None,
        "stroke": "#fffb0e",
        "stroke_width": 6,
        "dash_array": "dotted",
    },
)
p.arrow(target=(m45.ra, m45.dec))

p.export("tutorial_08.svg")
