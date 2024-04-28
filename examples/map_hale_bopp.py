from skyfield.api import load
from skyfield.data import mpc
from skyfield.constants import GM_SUN_Pitjeva_2005_km3_s2 as GM_SUN

from starplot import MapPlot, Projection
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

# Find the RA/DEC of comet for every 8 days starting on March 18, 1997
radecs = []
for day in range(0, 32, 8):
    t = ts.utc(1997, 3, 18 + day)
    ra, dec, distance = earth.at(t).observe(comet).radec()
    radecs.append((t, ra.hours, dec.degrees))

# Now let's plot the data on a map!
style = PlotStyle().extend(
    extensions.BLUE_DARK,
    extensions.MAP,
    {
        "star": {
            "label": {
                "font_size": 9,
                "font_weight": "normal",
            }
        },
        "legend": {
            "location": "lower center",
        },
    },
)
style.legend.location = "lower center"

p = MapPlot(
    projection=Projection.STEREO_NORTH,
    # to make plots that are centered around the 0h equinox, you can
    # set the max RA to a number over 24 which will determine how
    # far past 0h the plot will extend. For example, here we set
    # the max RA to 28, so this plot will have an RA extent from 23h to 4h
    ra_min=23,
    ra_max=28,
    dec_min=14,
    dec_max=60,
    style=style,
    resolution=2800,
)

# Plot the comet markers first, to ensure their labels are plotted
for t, ra, dec in radecs:
    label = f"{t.utc.month}/{t.utc.day}/{t.utc.year % 100}"
    p.marker(
        ra=ra,
        dec=dec,
        label=label,
        legend_label="Hale-Bopp Comet",
        style={
            "marker": {
                "size": 16,
                "symbol": "circle",
                "fill": "full",
                "color": "hsl(358, 78%, 58%)",
                "edge_color": "hsl(358, 78%, 42%)",
                "alpha": 0.64,
                "zorder": 4096,
            },
            "label": {
                "font_size": 17,
                "font_weight": "bold",
                "font_color": "hsl(60, 70%, 72%)",
                "zorder": 4096,
            },
        },
    )

p.gridlines(labels=False)
p.stars(mag=8)
p.constellations()
p.constellation_borders()
p.nebula(mag=8, labels=None)
p.open_clusters(mag=8, labels=None)
p.galaxies(mag=8, labels=None)
p.milky_way()
p.legend()

p.export("map_hale_bopp.png", padding=0.2)
