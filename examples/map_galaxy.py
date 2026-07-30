from starplot import _, GalaxyPlot, DSO
from starplot.styles import PlotStyle, extensions


style = PlotStyle().extend(
    extensions.BLUE_NIGHT,
    extensions.MAP,
    {
        "figure": {
            "padding": 60,
        }
    },
)

p = GalaxyPlot(
    style=style,
    resolution=5000,
    scale=0.83,
)
p.gridlines()

p.galactic_equator(num_labels=2)
p.celestial_equator(num_labels=2)
p.ecliptic(num_labels=2)

p.milky_way()

p.stars(
    where=[_.magnitude < 7],
    where_labels=[False],
    size_fn=lambda star: 8 - star.magnitude,
    style__marker__edge_color="#c5c5c5",
)

lmc = DSO.get(name="ESO056-115")
smc = DSO.get(name="NGC0292")
mc_style = {
    "font_color": "#acc2e0",
    "font_size": 42,
    "font_weight": 700,
    "border_width": 8,
    "border_color": "#1e232a",
}

p.text(
    "LMC",
    ra=lmc.ra,
    dec=lmc.dec,
    style=mc_style,
)

p.text(
    "SMC",
    ra=smc.ra,
    dec=smc.dec,
    style=mc_style,
)

p.open_clusters(
    where=[(_.magnitude < 16) | (_.magnitude.isnull())],
    where_labels=[False],
    where_true_size=[False],
)
p.legend()

p.title("Open Clusters Around the Milky Way", style__font_size=86)

p.export("map_galaxy.png")
