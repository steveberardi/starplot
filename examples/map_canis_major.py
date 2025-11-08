from starplot import MapPlot, Miller, Constellation, _
from starplot.styles import PlotStyle, extensions

style = PlotStyle().extend(
    extensions.BLUE_NIGHT,
    extensions.MAP,
)
canis_major = Constellation.get(name="Canis Major")
p = MapPlot(
    projection=Miller(),
    ra_min=6.19 * 15,
    ra_max=7.47 * 15,
    dec_min=-33.3,
    dec_max=-10.9,
    style=style,
    resolution=3400,
    clip_path=canis_major.boundary,
    scale=1.2,
)
p.constellations(
    where=[_.iau_id == "cma"],
)
p.constellation_borders()
p.open_clusters(where=[_.magnitude < 9], true_size=False)
p.nebula(where=[_.magnitude < 9], true_size=False)
p.stars(where=[_.magnitude < 9], where_labels=[_.magnitude < 4], bayer_labels=True)
p.constellation_labels()

p.ax.set_axis_off()  # hide the axis background that's outside the clip path

p.export("map_canis_major.png", padding=1)
