import pytest

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
