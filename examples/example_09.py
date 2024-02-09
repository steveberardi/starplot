from datetime import datetime
from pytz import timezone
from starplot import MapPlot, Projection
from starplot.styles import PlotStyle, extensions, MarkerSymbolEnum

style = PlotStyle().extend(
    extensions.BLUE_MEDIUM,
    extensions.MAP,
)

tz = timezone("Europe/Amsterdam")
dt = datetime(2024, 1, 20, 22, 00, tzinfo=tz)  # July 13, 2023 at 10pm PT

# With a Stereographic projection you can set the center point
# With STEREO_NORTH it is the northpole
# With STEREO_SOUTH it is the south pole
# here you cn choose here it is set on the equator
# note tha this center of the projection can be outside of the map bounds you set
p = MapPlot(
    projection=Projection.STEREOGRAPHIC,
    lat=0,
    lon=0,
    dt = dt,
    ra_min=0,
    ra_max=6,
    dec_min=-40,
    dec_max=60,
    limiting_magnitude=3.6,
    style=style,
    resolution=1400,
    dso_types=[],  # this is one way to hide all deep sky objects
)

p.plot_horizon() # plot a circle on the map where the horizon is for this (lat, lon)
p.export("09_stereographic.png", padding=0.2)
