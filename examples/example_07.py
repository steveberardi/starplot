from skyfield.api import load
from skyfield.data import mpc
from skyfield.constants import GM_SUN_Pitjeva_2005_km3_s2 as GM_SUN

from starplot import MapPlot, Projection, SkyObject
from starplot.styles import PlotStyle, extensions

# First, we use Skyfield to get comet data
# Code adapted from: https://rhodesmill.org/skyfield/kepler-orbits.html#comets
with load.open(mpc.COMET_URL) as f:
    comets = mpc.load_comets_dataframe(f)

# Keep only the most recent orbit for each comet,
# and index by designation for fast lookup.
comets = (
    comets.sort_values("reference")
    .groupby("designation", as_index=False)
    .last()
    .set_index("designation", drop=False)
)

# Find Hale-Bopp
row = comets.loc["C/1995 O1 (Hale-Bopp)"]

ts = load.timescale()
eph = load("de421.bsp")
sun, earth = eph["sun"], eph["earth"]
comet = sun + mpc.comet_orbit(row, ts, GM_SUN)

# Find the RA/DEC of comet for every 4 days starting on March 20, 1997
radecs = []
for day in range(0, 28, 4):
    t = ts.utc(1997, 3, 20 + day)
    ra, dec, distance = earth.at(t).observe(comet).radec()
    radecs.append((t, ra.hours, dec.degrees))

# Now let's plot the data on a map!
style = PlotStyle().extend(
    extensions.BLUE_LIGHT,
    extensions.MAP,
)
style.legend.location = "lower right"
style.legend.num_columns = 1

p = MapPlot(
    projection=Projection.STEREO_NORTH,
    # to make plots that are centered around the 0h equinox, you can
    # set the max RA to a number over 24 which will determine how
    # far past 0h the plot will extend. For example, here we set
    # the max RA to 28, so this plot will have an RA extent from 23h to 4h
    ra_min=23,
    ra_max=28,
    dec_min=30,
    dec_max=50,
    limiting_magnitude=6.2,
    style=style,
    resolution=2000,
)

for t, ra, dec in radecs:
    label = f"{t.utc.month}/{t.utc.day}/{t.utc.year % 100}"
    p.plot_object(
        SkyObject(
            name=label,
            legend_label="Hale-Bopp Comet",
            ra=ra,
            dec=dec,
            style={
                "marker": {
                    "size": 12,
                    "symbol": "o",
                    "fill": "full",
                    "color": "#ff6868",
                    "alpha": 0.8,
                    "zorder": 4096,
                },
                "label": {
                    "font_size": 13,
                    "font_weight": "bold",
                    "font_color": "#3c6daa",
                    "zorder": 4096,
                },
            },
        )
    )

# refresh the legend so the Hale-Bopp marker is included
p.refresh_legend()

p.export("07_map_hale_bopp.png", padding=0.2)
