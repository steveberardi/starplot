from starplot import MapPlot, Projection, SkyObject
from starplot.styles import PlotStyle, extensions

style = PlotStyle().extend(
    extensions.BLUE_LIGHT,
    extensions.MAP,
    {
        "bayer_labels": {
            "font_name": "GFS Didot",  # use a better font for Greek letters
            "font_size": 7,
            "font_alpha": 0.9,
        },
        "legend": {
            "location": "lower right",  # show legend inside map
            "num_columns": 1,
            "background_alpha": 1,
        },
    },
)
style.star.label.font_size = 11

p = MapPlot(
    projection=Projection.MERCATOR,
    ra_min=3.6,
    ra_max=7.8,
    dec_min=-16,
    dec_max=23.6,
    style=style,
    resolution=3600,
)

p.plot_stars(limiting_magnitude=9)
p.plot_dsos(limiting_magnitude=9, plot_null_magnitudes=True)
p.plot_constellations()
p.plot_constellation_borders()
p.plot_milky_way()
p.plot_ecliptic()

p.plot_object(
    SkyObject(
        name="M42",
        ra=5.58333,
        dec=-4.61,
        style={
            "marker": {
                "size": 10,
                "symbol": "circle_cross",
                "fill": "full",
                "color": "#ff6868",
                "alpha": 1,
                "zorder": 4096,
            },
            "label": {
                "font_size": 10,
                "font_weight": "bold",
                "font_color": "darkred",
                "zorder": 4096,
            },
        },
    )
)

p.refresh_legend()

p.export("03_map_orion.png", padding=0.5)
