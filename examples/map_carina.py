from starplot import MapPlot, Equidistant, _
from starplot.styles import PlotStyle, extensions

style = PlotStyle().extend(
    extensions.BLUE_MEDIUM,
    extensions.MAP,
)

p = MapPlot(
    projection=Equidistant(center_ra=11 * 15),
    ra_min=10 * 15,
    ra_max=12 * 15,
    dec_min=-70,
    dec_max=-55,
    style=style,
    resolution=3600,
    scale=1.4,
)

p.gridlines(
    ra_locations=[d for d in range(8 * 15, 14 * 15, 5)],
    dec_locations=[d for d in range(-50, -80, -2)],
    ra_formatter_fn=lambda ra: f"{round(ra * 15)}\u00B0",
)
p.constellations()
p.constellation_borders()

p.stars(where=[_.magnitude < 9], bayer_labels=True, where_labels=[_.magnitude < 5])


def dso_label(d):
    if d.common_names:
        return d.common_names[0]
    if d.ngc:
        return d.ngc
    if d.ic:
        return f"IC{d.ic}"
    return d.name


mag_filters = (_.magnitude < 11) | (_.magnitude.isnull())

p.open_clusters(
    where=[_.size < 0.2, _.magnitude < 11],
    where_labels=[False],
    label_fn=dso_label,
    true_size=False,
)

with p.style.dso_open_cluster as oc:
    oc.label.font_size = 26
    oc.label.font_weight = "heavy"
    p.open_clusters(
        # plot larger clusters as their true apparent size
        where=[_.size > 0.2, mag_filters],
        label_fn=dso_label,
    )

p.nebula(
    where=[mag_filters, _.size < 0.2],
    label_fn=dso_label,
    true_size=False,
)
with p.style.dso_nebula as neb:
    neb.label.font_size = 26
    neb.label.font_weight = "heavy"
    p.nebula(
        where=[mag_filters, _.size > 0.2],
        label_fn=dso_label,
    )

p.galaxies(
    where=[mag_filters],
    label_fn=dso_label,
    true_size=False,
)

p.constellation_labels()

p.legend(
    style__alignment="left",
    style__location="outside right upper",
    style__padding_x=-250,
    style__num_columns=1,
)
p.star_magnitude_scale(
    style__alignment="left",
    style__num_columns=1,
    add_to_legend=True,
    start=0,
    stop=9,
    step=1,
)

p.export("map_carina.png", padding=0.5)
