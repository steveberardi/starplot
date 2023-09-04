from pathlib import Path
from datetime import datetime

from pytz import timezone

import pytest

from starplot import styles
from starplot.map import MapPlot, Projection
from starplot.models import SkyObject

from .utils import assert_hashes_equal

HERE = Path(__file__).resolve().parent
DATA_PATH = HERE / "data"


@pytest.fixture()
def map_plot_mercator():
    # returns a mercator plot of Orion
    yield MapPlot(
        projection=Projection.MERCATOR,
        ra_min=3.6,
        ra_max=7.8,
        dec_min=-16,
        dec_max=24,
        limiting_magnitude=7.2,
        style=styles.MAP_BLUE_LIGHT,
        resolution=2000,
    )


@pytest.fixture()
def map_plot_stereo_north():
    yield MapPlot(
        projection=Projection.STEREO_NORTH,
        ra_min=17,
        ra_max=20,
        dec_min=30,
        dec_max=55,
        limiting_magnitude=12.0,
        style=styles.MAP_BLUE_LIGHT,
        resolution=2000,
    )


def test_map_plot_mercator_base(map_plot_mercator):
    filename = DATA_PATH / "actual-mercator-base.png"
    map_plot_mercator.export(filename)
    assert_hashes_equal(filename, DATA_PATH / "expected-mercator-base.png")


def test_map_plot_mercator_with_extra_object(map_plot_mercator):
    filename = DATA_PATH / "actual-mercator-extra.png"
    map_plot_mercator.plot_object(
        SkyObject(
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
    map_plot_mercator.export(filename)
    assert_hashes_equal(filename, DATA_PATH / "expected-mercator-extra.png")


def test_map_plot_stereo_base(map_plot_stereo_north):
    filename = DATA_PATH / "actual-stereo-north-base.png"
    map_plot_stereo_north.export(filename)
    assert_hashes_equal(filename, DATA_PATH / "expected-stereo-north-base.png")


def test_map_plot_stereo_with_extra_object(map_plot_stereo_north):
    filename = DATA_PATH / "actual-stereo-north-extra.png"

    map_plot_stereo_north.plot_object(
        SkyObject(
            name="M57",
            ra=18.885,
            dec=33.03,
            style={
                "marker": {
                    "size": 10,
                    "symbol": "s",
                    "fill": "full",
                    "color": "red",
                    "alpha": 0.6,
                }
            },
        )
    )
    map_plot_stereo_north.export(filename)
    assert_hashes_equal(filename, DATA_PATH / "expected-stereo-north-extra.png")


def test_map_plot_with_planets():
    filename = DATA_PATH / "actual-mercator-planets.png"
    dt = timezone("UTC").localize(datetime(2023, 8, 27, 23, 0, 0, 0))

    style = styles.MAP_BLUE_LIGHT
    style.bayer_labels.visible = False
    style.star.label.visible = False
    style.constellation.label.visible = False
    style.ecliptic.label.visible = False
    style.celestial_equator.label.visible = False

    p = MapPlot(
        projection=Projection.MERCATOR,
        ra_min=0,
        ra_max=24,
        dec_min=-70,
        dec_max=70,
        dt=dt,
        limiting_magnitude=3,
        include_planets=True,
        hide_colliding_labels=False,
        style=style,
        resolution=2600,
    )
    p.export(filename)

    assert_hashes_equal(filename, DATA_PATH / "expected-mercator-planets.png")
