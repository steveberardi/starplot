from datetime import datetime

import pytest

from pytz import timezone

from starplot.map import MapPlot, Projection


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


def test_map_objects_list():
    p = MapPlot(
        projection=Projection.MERCATOR,
        ra_min=8.3 * 15,
        ra_max=8.8 * 15,
        dec_min=19.4,
        dec_max=19.8,
    )
    p.open_clusters()
    assert "NGC2632" in [d.name for d in p.objects.dsos]

    p.stars(mag=8)
    assert 42578 in [s.hip for s in p.objects.stars]

    assert p.objects.moon is None
    assert len(p.objects.planets) == 0


def test_map_objects_list_planets():
    dt = timezone("UTC").localize(datetime(2023, 8, 27, 23, 0, 0, 0))

    p = MapPlot(
        projection=Projection.MILLER,
        ra_min=0,
        ra_max=24 * 15,
        dec_min=-40,
        dec_max=40,
        dt=dt,
    )
    p.planets()
    p.sun()
    p.moon()

    assert p.objects.moon.ra == 292.53617734161276
    assert p.objects.moon.dt == dt

    assert p.objects.sun.ra == 155.98273726181148
    assert p.objects.sun.dt == dt

    assert len(p.objects.planets) == 8


def test_marker_no_label():
    p = MapPlot(projection=Projection.MERCATOR)
    p.marker(ra=150, dec=0, style__marker__color="blue")
