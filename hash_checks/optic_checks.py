from pathlib import Path
from datetime import datetime

from pytz import timezone

from starplot import styles, optics, OpticPlot, callables, Moon, _

HERE = Path(__file__).resolve().parent
DATA_PATH = HERE / "data"

dt_dec_16 = datetime.now(timezone("US/Pacific")).replace(2023, 12, 16, 21, 0, 0, 0)
dt_april_8 = datetime.now(timezone("US/Pacific")).replace(2024, 4, 8, 11, 7, 0, 0)

style_light = styles.PlotStyle().extend(
    styles.extensions.GRAYSCALE,
    styles.extensions.OPTIC,
)
style_dark = styles.PlotStyle().extend(
    styles.extensions.GRAYSCALE_DARK,
    styles.extensions.OPTIC,
)
style_blue = styles.PlotStyle().extend(
    styles.extensions.BLUE_DARK,
    styles.extensions.OPTIC,
)

POWAY = {"lat": 32.97, "lon": -117.038611}

plot_kwargs = dict(
    resolution=2048,
    autoscale=True,
)


def check_optic_polaris_binoculars():
    optic_plot = OpticPlot(
        # Polaris
        ra=2.51667 * 15,
        dec=89.26,
        lat=32.97,
        lon=-117.038611,
        # 10x binoculars
        optic=optics.Binoculars(
            magnification=10,
            fov=65,
        ),
        dt=dt_dec_16,
        style=style_dark,
        **plot_kwargs,
    )
    optic_plot.stars(where=[_.magnitude < 14])
    optic_plot.info()
    filename = DATA_PATH / "optic-binoculars-polaris.png"
    optic_plot.export(filename)
    return filename


def check_optic_orion_nebula_refractor():
    optic_plot = OpticPlot(
        # Orion Nebula
        ra=5.583 * 15,
        dec=-5.383,
        lat=32.97,
        lon=-117.038611,
        # TV-85 with ES 14mm 82deg
        optic=optics.Refractor(
            focal_length=600,
            eyepiece_focal_length=14,
            eyepiece_fov=82,
        ),
        dt=dt_dec_16,
        style=style_dark,
        **plot_kwargs,
    )
    optic_plot.stars(where=[_.magnitude < 12])
    optic_plot.nebula()
    optic_plot.info()
    filename = DATA_PATH / "optic-orion-nebula-refractor.png"
    optic_plot.export(filename)
    return filename


def check_optic_wrapping():
    optic_plot = OpticPlot(
        ra=23.99 * 15,
        dec=17.573889,
        lat=32.97,
        lon=-117.038611,
        # use binoculars for a wide TFOV
        optic=optics.Binoculars(
            magnification=8,
            fov=65,
        ),
        dt=dt_dec_16,
        style=style_blue,
        **plot_kwargs,
    )
    optic_plot.stars(
        where=[_.magnitude < 8],
        style__marker__symbol="star",
        style__marker__size=600,
    )
    optic_plot.rectangle(
        center=(23.9 * 15, 17.5),
        height_degrees=1,
        width_degrees=2,
        style__fill_color="red",
    )
    optic_plot.info()
    filename = DATA_PATH / "optic-wrapping.png"
    optic_plot.export(filename)
    return filename


def check_optic_clipping():
    optic_plot = OpticPlot(
        # Orion Nebula
        ra=5.583 * 15,
        dec=-5.383,
        lat=32.97,
        lon=-117.038611,
        # TV-85
        optic=optics.Scope(
            focal_length=600,
            eyepiece_focal_length=8,
            eyepiece_fov=82,
        ),
        dt=dt_dec_16,
        style=style_blue,
        **plot_kwargs,
    )
    optic_plot.stars(where=[_.magnitude < 12])
    optic_plot.dsos(sql="select * from _ where magnitude < 8.1", labels=None)
    optic_plot.nebula()
    optic_plot.title("Orion Nebula")
    filename = DATA_PATH / "optic-clipping.png"
    optic_plot.export(filename, padding=0.4)
    return filename


def check_optic_m45_binoculars():
    optic_plot = OpticPlot(
        # M45
        ra=3.7836111111 * 15,
        dec=24.1166666667,
        lat=32.97,
        lon=-117.038611,
        # 10x binoculars
        optic=optics.Binoculars(
            magnification=10,
            fov=65,
        ),
        dt=dt_dec_16,
        style=style_dark,
        **plot_kwargs,
    )
    optic_plot.stars(where=[_.magnitude < 12])
    optic_plot.info()
    filename = DATA_PATH / "optic-m45-binoculars.png"
    optic_plot.export(filename)
    return filename


def check_optic_m45_scope():
    optic_plot = OpticPlot(
        # M45
        ra=3.7836111111 * 15,
        dec=24.1166666667,
        lat=32.97,
        lon=-117.038611,
        optic=optics.Scope(
            focal_length=600,
            eyepiece_focal_length=14,
            eyepiece_fov=82,
        ),
        dt=dt_dec_16,
        style=style_dark,
        **plot_kwargs,
    )
    optic_plot.stars(
        where=[_.magnitude < 12],
        color_fn=callables.color_by_bv,
        style={"label": {"font_color": "#7df597"}},
    )
    optic_plot.info()
    filename = DATA_PATH / "optic-m45-scope.png"
    optic_plot.export(filename)
    return filename


def check_optic_m45_reflector():
    optic_plot = OpticPlot(
        # M45
        ra=3.7836111111 * 15,
        dec=24.1166666667,
        lat=32.97,
        lon=-117.038611,
        optic=optics.Reflector(
            focal_length=600,
            eyepiece_focal_length=14,
            eyepiece_fov=82,
        ),
        dt=dt_dec_16,
        style=style_dark,
        **plot_kwargs,
    )
    optic_plot.stars(where=[_.magnitude < 12])
    optic_plot.info()
    filename = DATA_PATH / "optic-m45-reflector.png"
    optic_plot.export(filename)
    return filename


def check_optic_m45_camera():
    optic_plot = OpticPlot(
        # M45
        ra=3.7836111111 * 15,
        dec=24.1166666667,
        lat=32.97,
        lon=-117.038611,
        # Fuji X-T2
        optic=optics.Camera(
            sensor_height=15.6,
            sensor_width=23.6,
            lens_focal_length=430,
        ),
        dt=dt_dec_16,
        style=style_dark,
        **plot_kwargs,
    )
    optic_plot.stars(
        where=[_.magnitude < 12], style__marker__symbol=styles.MarkerSymbolEnum.STAR
    )
    optic_plot.info()
    filename = DATA_PATH / "optic-m45-camera.png"
    optic_plot.export(filename)
    optic_plot.close_fig()
    return filename


def check_optic_camera_rotated():
    optic_plot = OpticPlot(
        # M45
        ra=3.7836111111 * 15,
        dec=24.1166666667,
        lat=32.97,
        lon=-117.038611,
        # Fuji X-T2
        optic=optics.Camera(
            sensor_height=15.6,
            sensor_width=23.6,
            lens_focal_length=430,
            rotation=40,
        ),
        dt=dt_dec_16,
        style=style_dark,
        **plot_kwargs,
    )
    optic_plot.stars(where=[_.magnitude < 12])
    optic_plot.info()
    filename = DATA_PATH / "optic-camera-rotated-m45.png"
    optic_plot.export(filename)
    optic_plot.close_fig()
    return filename


def check_optic_solar_eclipse_binoculars():
    optic_plot = OpticPlot(
        lat=33.363484,
        lon=-116.836394,
        ra=1.16667 * 15,
        dec=7.45,
        optic=optics.Binoculars(magnification=12, fov=65),
        dt=dt_april_8,
        style=styles.PlotStyle().extend(
            styles.extensions.BLUE_MEDIUM,
        ),
        **plot_kwargs,
    )
    optic_plot.stars(where=[_.magnitude < 14])
    optic_plot.moon(true_size=True, show_phase=True)
    optic_plot.sun(true_size=True)
    filename = DATA_PATH / "optic-binoculars-eclipse.png"
    optic_plot.export(filename)
    optic_plot.close_fig()
    return filename


def check_optic_moon_phase_waxing_crescent():
    m = Moon.get(dt=dt_dec_16, **POWAY)
    optic_plot = m.create_optic(
        **POWAY,
        optic=optics.Binoculars(
            magnification=20,
            fov=65,
        ),
        dt=dt_dec_16,
        style=style_dark,
        raise_on_below_horizon=False,
        **plot_kwargs,
    )
    optic_plot.moon(
        true_size=True,
        show_phase=True,
        label=None,
    )
    filename = DATA_PATH / "optic-moon-phase-waxing-crescent.png"
    optic_plot.export(filename)
    optic_plot.close_fig()
    return filename


def check_optic_moon_phase_new():
    m = Moon.get(dt=dt_april_8, **POWAY)
    optic_plot = m.create_optic(
        **POWAY,
        optic=optics.Binoculars(
            magnification=30,
            fov=65,
        ),
        dt=dt_april_8,
        style=style_light,
        raise_on_below_horizon=False,
        **plot_kwargs,
    )
    optic_plot.moon(
        true_size=True,
        show_phase=True,
        label=None,
    )
    filename = DATA_PATH / "optic-moon-phase-new.png"
    optic_plot.export(filename)
    optic_plot.close_fig()
    return filename


def check_optic_moon_phase_full():
    dt_full_moon = datetime.now(timezone("US/Pacific")).replace(2024, 4, 23, 11, 7, 0)
    m = Moon.get(dt=dt_full_moon, **POWAY)
    optic_plot = m.create_optic(
        **POWAY,
        optic=optics.Binoculars(
            magnification=20,
            fov=65,
        ),
        dt=dt_full_moon,
        style=style_dark,
        raise_on_below_horizon=False,
        **plot_kwargs,
    )
    optic_plot.moon(
        true_size=True,
        show_phase=True,
        label=None,
    )
    filename = DATA_PATH / "optic-moon-phase-full.png"
    optic_plot.export(filename)
    optic_plot.close_fig()
    return filename
