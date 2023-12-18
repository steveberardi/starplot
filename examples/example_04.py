from starplot import MapPlot, Projection
from starplot.styles import PlotStyle, extensions

style = PlotStyle().extend(
    extensions.MINIMAL,
    extensions.GRAYSCALE,
    extensions.MAP,
)

p = MapPlot(
    projection=Projection.STEREO_NORTH,
    ra_min=54.5 / 15,
    ra_max=58.5 / 15,
    dec_min=23,
    dec_max=25.4,
    limiting_magnitude=12,
    style=style,
    resolution=1400,
    star_catalog="tycho-1",
)
p.plot_scope_fov(
    ra=3.7836111111,
    dec=24.1166666667,
    scope_focal_length=600,
    eyepiece_focal_length=14,
    eyepiece_fov=82,
)

p.ax.set_title("M45 :: TV-85 / 14mm @ 82deg")

p.export("04_map_m45_scope.png", padding=0.3)
