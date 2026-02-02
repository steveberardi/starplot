from starplot import MapPlot, Equidistant, CollisionHandler, _
from starplot.styles import PlotStyle, extensions, AnchorPointEnum

style = PlotStyle().extend(
    extensions.BLUE_MEDIUM,
    extensions.MAP,
    {
        "figure_background_color": "hsl(330, 44%, 20%)",
        "dso_galaxy": {
            "label": {
                "font_color": "hsl(330, 44%, 14%)",
                "font_weight": 200,
                "anchor_point": AnchorPointEnum.BOTTOM_CENTER.value,
            }
        },
    },
)

# Create a custom collision handler that ensures labels are ALWAYS plotted
collision_handler = CollisionHandler(
    # always plot an object's label, even if it collides with other labels or markers:
    plot_on_fail=True,
    # only try plotting object labels once:
    attempts=1,
)

p = MapPlot(
    projection=Equidistant(center_ra=11 * 15),
    ra_min=12 * 15,
    ra_max=13 * 15,
    dec_min=8,
    dec_max=18,
    style=style,
    resolution=3000,
    scale=1,
    collision_handler=collision_handler,
)
p.title("Virgo Cluster", style__font_color="hsl(330, 44%, 92%)")
p.stars(where=[_.magnitude < 12], where_labels=[False])
p.galaxies(
    where=[
        (_.magnitude < 12) | (_.magnitude.isnull()),
    ],
    where_true_size=[False],
)
p.export("map_virgo_cluster.png", padding=0.8)
