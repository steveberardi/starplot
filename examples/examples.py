# examples from documentation


def example_1_create_star_chart():
    from datetime import datetime
    from pytz import timezone
    import starplot as sp

    tz = timezone("America/Los_Angeles")

    p = sp.ZenithPlot(
        lat=33.363484,
        lon=-116.836394,
        dt=tz.localize(datetime.now().replace(hour=22)),
        limiting_magnitude=4.6,
        style=sp.styles.BLUE,
        resolution=2000,
    )
    p.export("01_star_chart.png")


def example_2_create_star_chart_extra():
    from datetime import datetime
    from pytz import timezone
    import starplot as sp

    tz = timezone("America/Los_Angeles")

    p = sp.ZenithPlot(
        lat=32.97,
        lon=-117.038611,
        dt=tz.localize(datetime.now().replace(hour=22)),
        limiting_magnitude=4.6,
        style=sp.styles.GRAYSCALE,
        resolution=2000,
    )
    p.plot_object(
        sp.SkyObject(
            name="Mel 111",
            ra=12.36,
            dec=25.85,
            style={
                "marker": {"size": 10, "symbol": "*", "fill": "full", "color": "red"}
            },
        )
    )
    p.export("02_star_chart_extra.png")


def example_3_create_map_orion():
    import starplot as sp

    style = sp.styles.MAP_BLUE.extend(
        {
            "bayer_labels": {
                "font_name": "GFS Didot",  # use a better font for Greek letters
                "font_size": 7,
                "font_alpha": 0.9,
            },
        }
    )
    style.star.label.font_size = 11

    p = sp.MapPlot(
        projection=sp.Projection.MERCATOR,
        ra_min=3.6,
        ra_max=7.8,
        dec_min=-16,
        dec_max=23.6,
        limiting_magnitude=7.2,
        style=style,
        resolution=4000,
    )
    p.plot_object(
        sp.SkyObject(
            name="M42",
            ra=5.58333,
            dec=-4.61,
            style={
                "marker": {
                    "size": 10,
                    "symbol": "s",
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
    p.export("03_map_orion.svg", format="svg", padding=0.5)


def example_style():
    import starplot as sp

    sp.styles.MAP_BLUE.dump_to_file("blue.yml")


# Documented Examples
example_1_create_star_chart()
example_2_create_star_chart_extra()
example_3_create_map_orion()
example_style()
