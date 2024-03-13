from starplot import MapPlot, Projection
from starplot.styles import PlotStyle, extensions

style = PlotStyle().extend(
    extensions.GRAYSCALE,
    extensions.MAP,
)
style.star.marker.size = 60

p = MapPlot(
    projection=Projection.STEREO_NORTH,
    ra_min=54.5 / 15,
    ra_max=58.5 / 15,
    dec_min=22.5,
    dec_max=25.5,
    style=style,
    resolution=1400,
)
p.stars(
    mag=14,
    catalog="tycho-1",
)
p.dsos(mag=8, labels=None)
p.scope_fov(
    ra=3.7912778,
    dec=24.1052778,
    scope_focal_length=600,
    eyepiece_focal_length=14,
    eyepiece_fov=82,
)
p.title("M45 :: TV-85 / 14mm @ 82deg")
p.export("04_map_m45_scope.png", padding=0.3)
