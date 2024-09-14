from starplot import MapPlot, Projection, Constellation
from starplot.styles import PlotStyle, extensions

style = PlotStyle().extend(
    extensions.CB_WONG,
    extensions.MAP,
    {
        "star": {"marker": {"size": 40}, "label": {"font_size": 13}},
        "bayer_labels": {
            "font_name": "GFS Didot",  # use a better font for Greek letters
            "font_size": 10,
            "font_alpha": 0.9,
        },
        "dso_open_cluster": {"marker": {"size": 20}, "label": {"font_size": 10}},
    },
)
canis_major = Constellation.get(name="Canis Major")
p = MapPlot(
    projection=Projection.MILLER,
    ra_min=6,
    ra_max=7.6,
    dec_min=-35,
    dec_max=-9,
    style=style,
    resolution=2000,
    clip_path=canis_major.boundary,
)
p.open_clusters(mag=8, true_size=False, label_fn=lambda d: f"{d.ngc}")
p.stars(mag=9, bayer_labels=True, catalog="big-sky-mag11")
p.constellations(
    where=[Constellation.iau_id == "cma"],
    style__line__width=7,
    style__label__font_size=18,
)
p.constellation_borders()
p.ax.set_axis_off()
p.export("map_canis_major.png", padding=0, transparent=True)
