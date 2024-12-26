from starplot import MapPlot, Projection, Constellation
from starplot.styles import PlotStyle, extensions

style = PlotStyle().extend(
    extensions.BLUE_LIGHT,
    extensions.MAP,
)
canis_major = Constellation.get(name="Canis Major")
p = MapPlot(
    projection=Projection.MILLER,
    ra_min=6,
    ra_max=7.6,
    dec_min=-35,
    dec_max=-9,
    style=style,
    resolution=3600,
    clip_path=canis_major.boundary,
    scale=1.3,
)
p.constellations(
    where=[Constellation.iau_id == "cma"],
)
p.constellation_borders()
p.open_clusters(mag=8, true_size=False, label_fn=lambda d: f"{d.ngc}")
p.stars(mag=9, bayer_labels=True, catalog="big-sky-mag11")
p.constellation_labels()
p.ax.set_axis_off()
p.export("map_canis_major.png", padding=0, transparent=True)
