from pathlib import Path
from datetime import datetime

from pytz import timezone

from starplot import styles, optics, OpticPlot, callables

HERE = Path(__file__).resolve().parent
DATA_PATH = HERE / "data"

dt_dec_16 = datetime.now(timezone("US/Pacific")).replace(2023, 12, 16, 21, 0, 0)
dt_april_8 = datetime.now(timezone("US/Pacific")).replace(2024, 4, 8, 11, 7, 0)

optic_style = styles.PlotStyle().extend(
    styles.extensions.GRAYSCALE_DARK,
    styles.extensions.OPTIC,
)


def check_optic_polaris_binoculars():
    optic_plot = OpticPlot(
        # Polaris
        ra=2.51667,
        dec=89.26,
        lat=32.97,
        lon=-117.038611,
        # 10x binoculars
        optic=optics.Binoculars(
            magnification=10,
            fov=65,
        ),
        dt=dt_dec_16,
        style=optic_style,
        resolution=1600,
    )
    optic_plot.stars(mag=14)
    optic_plot.info()
    filename = DATA_PATH / "optic-binoculars-polaris.png"
    optic_plot.export(filename)
    return filename


def check_optic_solar_eclipse_binoculars():
    optic_plot = OpticPlot(
        lat=33.363484,
        lon=-116.836394,
        ra=1.16667,
        dec=7.45,
        optic=optics.Binoculars(magnification=8, fov=65),
        dt=dt_april_8,
        style=styles.PlotStyle().extend(
            styles.extensions.BLUE_MEDIUM,
            styles.extensions.ZENITH,
        ),
        resolution=2000,
    )
    optic_plot.stars(mag=14)
    optic_plot.moon(true_size=True)
    optic_plot.sun(true_size=True)
    filename = DATA_PATH / "optic-binoculars-eclipse.png"
    optic_plot.export(filename)
    return filename


def check_optic_double_cluster_refractor():
    optic_plot = OpticPlot(
        # double cluster
        ra=2.33,
        dec=57.14,
        lat=32.97,
        lon=-117.038611,
        # TV-85 with ES 14mm 82deg
        optic=optics.Refractor(
            focal_length=600,
            eyepiece_focal_length=14,
            eyepiece_fov=82,
        ),
        dt=dt_dec_16,
        style=optic_style,
        resolution=1600,
    )
    optic_plot.stars(mag=12)
    optic_plot.info()
    filename = DATA_PATH / "optic-double-cluster-refractor.png"
    optic_plot.export(filename)
    return filename


def check_optic_wrapping():
    style = optic_style.extend(
        {
            "star": {
                "marker": {
                    "symbol": "star",
                    "size": 90,
                }
            }
        }
    )
    optic_plot = OpticPlot(
        ra=23.99,
        dec=17.2738888889,
        lat=32.97,
        lon=-117.038611,
        # use binoculars for a wide TFOV
        optic=optics.Binoculars(
            magnification=8,
            fov=65,
        ),
        dt=dt_dec_16,
        style=style,
        resolution=1600,
    )
    optic_plot.stars(mag=12)
    optic_plot.info()
    filename = DATA_PATH / "optic-wrapping.png"
    optic_plot.export(filename)
    return filename


def check_optic_m45_binoculars():
    optic_plot = OpticPlot(
        # M45
        ra=3.7836111111,
        dec=24.1166666667,
        lat=32.97,
        lon=-117.038611,
        # 10x binoculars
        optic=optics.Binoculars(
            magnification=10,
            fov=65,
        ),
        dt=dt_dec_16,
        style=optic_style,
        resolution=1600,
    )
    optic_plot.stars(mag=12)
    optic_plot.info()
    filename = DATA_PATH / "optic-m45-binoculars.png"
    optic_plot.export(filename)
    return filename


def check_optic_m45_scope():
    optic_plot = OpticPlot(
        # M45
        ra=3.7836111111,
        dec=24.1166666667,
        lat=32.97,
        lon=-117.038611,
        optic=optics.Scope(
            focal_length=600,
            eyepiece_focal_length=14,
            eyepiece_fov=82,
        ),
        dt=dt_dec_16,
        style=optic_style,
        resolution=1600,
    )
    optic_plot.stars(
        mag=12,
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
        ra=3.7836111111,
        dec=24.1166666667,
        lat=32.97,
        lon=-117.038611,
        optic=optics.Reflector(
            focal_length=600,
            eyepiece_focal_length=14,
            eyepiece_fov=82,
        ),
        dt=dt_dec_16,
        style=optic_style,
        resolution=1600,
    )
    optic_plot.stars(mag=12)
    optic_plot.info()
    filename = DATA_PATH / "optic-m45-reflector.png"
    optic_plot.export(filename)
    return filename


def check_optic_m45_camera():
    optic_plot = OpticPlot(
        # M45
        ra=3.7836111111,
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
        style=optic_style,
        resolution=1600,
    )
    optic_plot.stars(mag=12, style__marker__symbol=styles.MarkerSymbolEnum.STAR)
    optic_plot.info()
    filename = DATA_PATH / "optic-m45-camera.png"
    optic_plot.export(filename)
    return filename


def check_optic_camera_rotated():
    optic_plot = OpticPlot(
        # M45
        ra=3.7836111111,
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
        style=optic_style,
        resolution=1600,
    )
    optic_plot.stars(mag=12)
    optic_plot.info()
    filename = DATA_PATH / "optic-camera-rotated-m45.png"
    optic_plot.export(filename)
    return filename
