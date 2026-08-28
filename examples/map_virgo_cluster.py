from starplot import CollisionHandler, Equidistant, MapPlot, _
from starplot.styles import AnchorPoint, PlotStyle, extensions

style = PlotStyle().extend(
    extensions.BLUE_MEDIUM,
    extensions.MAP,
    {
        "figure": {
            "background": {"fill": "hsl(330, 44%, 20%)"},
            "padding": 40,
        },
        "dso_galaxy": {
            "label": {
                "fill": "hsl(330, 44%, 14%)",
                "font_weight": 200,
                "anchor_point": AnchorPoint.BOTTOM_CENTER,
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
    point_label_handler=collision_handler,
)
p.title("Virgo Cluster", style__fill="hsl(330, 44%, 92%)")
p.stars(where=[_.magnitude < 12], where_labels=[False])
p.galaxies(
    where=[
        (_.magnitude < 12) | (_.magnitude.isnull()),
    ],
    where_true_size=[False],
)
p.export("map_virgo_cluster.png")
