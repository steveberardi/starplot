from pathlib import Path
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from starplot import styles, OpticPlot, callables, Moon, _, Satellite, Observer
from starplot.models import optics

HERE = Path(__file__).resolve().parent
DATA_PATH = HERE / "data"

tz = ZoneInfo("America/Los_Angeles")

dt_dec_16 = datetime(2023, 12, 16, 21, 0, 0, 0, tzinfo=tz)
dt_april_8 = datetime(2024, 4, 8, 11, 7, 0, 0, tzinfo=tz)

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

observer_dec_16_poway = Observer(
    dt=dt_dec_16,
    lat=32.97,
    lon=-117.038611,
)


def check_optic_polaris_binoculars():
    optic_plot = OpticPlot(
        # Polaris
        ra=2.51667 * 15,
        dec=89.26,
        # 10x binoculars
        optic=optics.Binoculars(
            magnification=10,
            fov=65,
        ),
        observer=observer_dec_16_poway,
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
        # TV-85 with ES 14mm 82deg
        optic=optics.Refractor(
            focal_length=600,
            eyepiece_focal_length=14,
            eyepiece_fov=82,
        ),
        observer=observer_dec_16_poway,
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
        # use binoculars for a wide TFOV
        optic=optics.Binoculars(
            magnification=8,
            fov=65,
        ),
        observer=observer_dec_16_poway,
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
        # TV-85
        optic=optics.Scope(
            focal_length=600,
            eyepiece_focal_length=8,
            eyepiece_fov=82,
        ),
        observer=observer_dec_16_poway,
        style=style_blue,
        **plot_kwargs,
    )
    optic_plot.stars(where=[_.magnitude < 12])
    optic_plot.dsos(sql="select * from _ where magnitude < 8.1", where_labels=[False])
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
        # 10x binoculars
        optic=optics.Binoculars(
            magnification=10,
            fov=65,
        ),
        observer=observer_dec_16_poway,
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
        optic=optics.Scope(
            focal_length=600,
            eyepiece_focal_length=14,
            eyepiece_fov=82,
        ),
        observer=observer_dec_16_poway,
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


def check_optic_m45_scope_gradient():
    style_gradient = style_dark.extend(styles.extensions.GRADIENT_PRE_DAWN)
    optic_plot = OpticPlot(
        # M45
        ra=3.7836111111 * 15,
        dec=24.1166666667,
        observer=observer_dec_16_poway,
        optic=optics.Scope(
            focal_length=600,
            eyepiece_focal_length=14,
            eyepiece_fov=82,
        ),
        style=style_gradient,
        **plot_kwargs,
    )
    optic_plot.stars(
        where=[_.magnitude < 12],
        color_fn=callables.color_by_bv,
        style={"label": {"font_color": "#7df597"}},
    )
    optic_plot.info()
    filename = DATA_PATH / "optic-m45-scope-gradient.png"
    optic_plot.export(filename)
    return filename


def check_optic_m45_reflector():
    optic_plot = OpticPlot(
        # M45
        ra=3.7836111111 * 15,
        dec=24.1166666667,
        optic=optics.Reflector(
            focal_length=600,
            eyepiece_focal_length=14,
            eyepiece_fov=82,
        ),
        observer=observer_dec_16_poway,
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
        # Fuji X-T2
        optic=optics.Camera(
            sensor_height=15.6,
            sensor_width=23.6,
            lens_focal_length=430,
        ),
        observer=observer_dec_16_poway,
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
        # Fuji X-T2
        optic=optics.Camera(
            sensor_height=15.6,
            sensor_width=23.6,
            lens_focal_length=430,
            rotation=40,
        ),
        observer=observer_dec_16_poway,
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
    observer = Observer(
        dt=dt_april_8,
        lat=33.363484,
        lon=-116.836394,
    )
    optic_plot = OpticPlot(
        ra=1.16667 * 15,
        dec=7.45,
        optic=optics.Binoculars(magnification=12, fov=65),
        observer=observer,
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
        optic=optics.Binoculars(
            magnification=20,
            fov=65,
        ),
        observer=observer_dec_16_poway,
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
    observer = Observer(
        dt=dt_april_8,
        **POWAY,
    )
    m = Moon.get(dt=dt_april_8, **POWAY)
    optic_plot = m.create_optic(
        optic=optics.Binoculars(
            magnification=30,
            fov=65,
        ),
        observer=observer,
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
    dt_full_moon = datetime(2024, 4, 23, 11, 7, 0, 0, tzinfo=tz)
    observer = Observer(
        dt=dt_full_moon,
        **POWAY,
    )
    m = Moon.get(dt=dt_full_moon, **POWAY)
    optic_plot = m.create_optic(
        optic=optics.Binoculars(
            magnification=20,
            fov=65,
        ),
        observer=observer,
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


def check_optic_iss_moon_transit():
    tz = ZoneInfo("US/Pacific")
    dt = datetime(2025, 12, 8, 8, 3, 16, tzinfo=tz)
    style = styles.PlotStyle().extend(
        styles.extensions.BLUE_DARK,
        styles.extensions.OPTIC,
    )

    observer = Observer(
        dt=dt,
        lat=33.0225027778,
        lon=-116.507025,
    )

    moon = Moon.get(dt=observer.dt, lat=observer.lat, lon=observer.lon)

    p = OpticPlot(
        ra=moon.ra,
        dec=moon.dec,
        observer=observer,
        optic=optics.Binoculars(
            magnification=15,
            fov=65,
        ),
        style=style,
        resolution=2400,
        autoscale=True,
    )
    p.moon(true_size=True, show_phase=True, label=None)

    iss = Satellite.from_tle(
        name="ISS (ZARYA)",
        line1="1 25544U 98067A   25312.42041502  .00013418  00000+0  24734-3 0  9990",
        line2="2 25544  51.6332 312.3676 0004093  47.8963 312.2373 15.49452868537539",
        lat=observer.lat,
        lon=observer.lon,
    )

    dt_start = observer.dt - timedelta(minutes=1)
    dt_end = observer.dt + timedelta(minutes=1)

    for sat in iss.trajectory(dt_start, dt_end, step=timedelta(seconds=1)):
        if sat.geometry.intersects(moon.geometry):
            marker_color = "red"
            symbol = "circle"
        else:
            marker_color = "gold"
            symbol = "plus"
        p.marker(
            sat.ra,
            sat.dec,
            style={
                "marker": {
                    "size": 70,
                    "symbol": symbol,
                    "color": marker_color,
                    "zorder": 5_000,
                },
            },
        )

    filename = DATA_PATH / "optic-iss-moon-transit.png"
    p.export(filename)
    p.close_fig()
    return filename
