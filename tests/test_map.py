from pathlib import Path
from datetime import datetime

from pytz import timezone

import pytest

from starplot import styles
from starplot.map import MapPlot, Projection

from .utils import colorhash, dhash

HERE = Path(__file__).resolve().parent
DATA_PATH = HERE / "data"


STYLE = styles.PlotStyle().extend(
    styles.extensions.BLUE_LIGHT,
    styles.extensions.MAP,
)
RESOLUTION = 3200


@pytest.fixture()
def map_plot_mercator():
    # returns a mercator plot of Orion
    p = MapPlot(
        projection=Projection.MERCATOR,
        ra_min=3.6,
        ra_max=7.8,
        dec_min=-16,
        dec_max=23.6,
        style=STYLE,
        resolution=RESOLUTION,
    )
    p.stars(mag=7.6, bayer_labels=True)
    p.dsos(mag=8, null=True, labels=None)
    p.milky_way()
    p.gridlines()
    p.ecliptic()
    p.celestial_equator()
    p.constellations()
    p.constellation_borders()

    yield p


@pytest.fixture()
def map_plot_stereo_north():
    p = MapPlot(
        projection=Projection.STEREO_NORTH,
        ra_min=17,
        ra_max=20,
        dec_min=30,
        dec_max=55,
        style=STYLE,
        resolution=RESOLUTION,
    )
    p.stars(mag=7.6, bayer_labels=True)
    p.dsos(mag=8, null=True, labels=None)
    p.milky_way()
    p.gridlines()
    p.constellations()
    p.constellation_borders()
    yield p


def test_map_plot_mercator_base(map_plot_mercator):
    filename = DATA_PATH / "map-mercator-base.png"
    map_plot_mercator.export(filename)
    assert dhash(filename) == "183b3a6e6e2e6c6c"
    assert colorhash(filename) == "07403000000"


def test_map_plot_mercator_extra(map_plot_mercator):
    filename = DATA_PATH / "map-mercator-extra.png"
    map_plot_mercator.marker(
        ra=4.5,
        dec=5,
        label="hello worldzz",
        style={
            "marker": {
                "size": 30,
                "symbol": "square",
                "fill": "full",
                "color": "#ff6868",
            },
        },
        legend_label="hello legend",
    )
    map_plot_mercator.circle(
        (7, -10),
        5,
        style=styles.PolygonStyle(
            fill_color="blue",
            alpha=0.14,
        ),
    )
    map_plot_mercator.legend()
    map_plot_mercator.export(filename, padding=0.5)
    assert dhash(filename) == "1c1b1a6b2e6c6c17"
    assert colorhash(filename) == "07c02000000"


def test_map_plot_stereo_base(map_plot_stereo_north):
    filename = DATA_PATH / "map-stereo-north-base.png"
    map_plot_stereo_north.export(filename)
    assert dhash(filename) == "627666f02c383416"
    assert colorhash(filename) == "071c0000000"


def test_map_plot_with_planets():
    filename = DATA_PATH / "map-mercator-planets.png"
    dt = timezone("UTC").localize(datetime(2023, 8, 27, 23, 0, 0, 0))

    p = MapPlot(
        projection=Projection.MILLER,
        ra_min=0,
        ra_max=24,
        dec_min=-70,
        dec_max=70,
        dt=dt,
        hide_colliding_labels=False,
        style=STYLE,
        resolution=RESOLUTION,
    )
    p.stars(mag=3, labels=None)
    p.planets()
    p.ecliptic()
    p.gridlines()
    p.export(filename)

    assert dhash(filename) == "4c681185cbb28a0c"
    assert colorhash(filename) == "07e00000000"


def test_map_plot_scope_bino_fov():
    filename = DATA_PATH / "map-scope-bino-fov.png"
    dt = timezone("UTC").localize(datetime(2023, 8, 27, 23, 0, 0, 0))

    style = styles.PlotStyle().extend(
        styles.extensions.GRAYSCALE,
        styles.extensions.MAP,
    )

    p = MapPlot(
        projection=Projection.STEREO_NORTH,
        ra_min=52 / 15,
        ra_max=62 / 15,
        dec_min=20,
        dec_max=28,
        dt=dt,
        style=style,
        resolution=1000,
        star_catalog="tycho-1",
    )
    p.stars(mag=12)
    p.scope_fov(
        ra=3.791278,
        dec=24.105278,
        scope_focal_length=600,
        eyepiece_focal_length=14,
        eyepiece_fov=82,
    )
    p.bino_fov(ra=3.791278, dec=24.105278, fov=65, magnification=10)
    p.title("M45 :: TV-85 / 14mm @ 82deg, 10x binos @ 65deg")
    p.export(filename, padding=0.3)

    assert dhash(filename) == "0b8eb2accca0828c"
    assert colorhash(filename) == "07400038000"


def test_map_plot_custom_stars():
    filename = DATA_PATH / "map-custom-stars.png"

    style = styles.PlotStyle().extend(
        styles.extensions.GRAYSCALE,
        styles.extensions.MAP,
    )
    style.star.marker.symbol = "star_8"
    style.star.marker.size = 60

    p = MapPlot(
        projection=Projection.MERCATOR,
        ra_min=3.6,
        ra_max=7.8,
        dec_min=-16,
        dec_max=24,
        style=style,
        resolution=RESOLUTION,
    )
    p.stars(mag=6)
    p.export(filename, padding=0.3)

    assert dhash(filename) == "5cb129ceae0e8408"
    assert colorhash(filename) == "07000000000"


def test_map_plot_wrapping():
    filename = DATA_PATH / "map-wrapping.png"

    style = styles.PlotStyle().extend(
        styles.extensions.GRAYSCALE,
        styles.extensions.MAP,
    )

    p = MapPlot(
        projection=Projection.STEREO_NORTH,
        ra_min=18,
        ra_max=26,
        dec_min=30,
        dec_max=50,
        style=style,
        resolution=RESOLUTION,
    )
    p.stars(mag=9)
    p.dsos(mag=9, null=True)
    p.gridlines()
    p.constellations()
    p.title("Andromeda + nebula + Vega")
    p.export(filename, padding=0.3)

    assert dhash(filename) == "17574e6d46432511"
    assert colorhash(filename) == "07000000000"


def test_map_radec_invalid():
    with pytest.raises(ValueError, match="ra_min must be less than ra_max"):
        MapPlot(
            projection=Projection.MERCATOR,
            ra_min=24,
            ra_max=8,
            dec_min=-16,
            dec_max=24,
        )

    with pytest.raises(ValueError, match="dec_min must be less than dec_max"):
        MapPlot(
            projection=Projection.MERCATOR,
            ra_min=8,
            ra_max=24,
            dec_min=50,
            dec_max=24,
        )


def test_map_mollweide():
    filename = DATA_PATH / "map-mollweide.png"

    style = styles.PlotStyle().extend(
        styles.extensions.GRAYSCALE,
        styles.extensions.MAP,
    )

    p = MapPlot(
        projection=Projection.MOLLWEIDE,
        style=style,
        resolution=RESOLUTION,
    )
    p.stars(mag=4.2, mag_labels=1.8)
    p.constellations()
    p.dsos(mag=4, null=True, labels=None)
    p.milky_way()
    p.gridlines(labels=False)
    p.export(filename, padding=0.1)

    assert dhash(filename) == "0b2b1b632b331707"
    assert colorhash(filename) == "07000000000"


# TODO : Add orthographic
# TODO : Add Zenith
