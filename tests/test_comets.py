from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from unittest.mock import patch, MagicMock

from starplot import Comet

from .utils import TEST_DATA_PATH

TZ_PT = ZoneInfo("America/Los_Angeles")

with open(TEST_DATA_PATH / "comets.txt", "rb") as comet_file:
    comet_data = comet_file.read()

mock_file_obj = MagicMock()
mock_file_obj.read.return_value = comet_data

mock_load = MagicMock()
mock_load.return_value.__enter__.return_value = mock_file_obj


@patch("starplot.models.comet.load.open", mock_load)
class TestComet:
    def test_comet_get(self):
        c2025_a6_lemmon = Comet.get(name="C/2025 A6 (Lemmon)")

        assert c2025_a6_lemmon.name == "C/2025 A6 (Lemmon)"

    def test_comet_all(self):
        comets = [c for c in Comet.all()]

        # there should only be two comets cause we're using an abridged test file
        assert len(comets) == 2

    def test_comet_get_at_date(self):
        dt = datetime(2025, 10, 21, 19, 0, tzinfo=TZ_PT)

        c2025_a6_lemmon = Comet.get(name="C/2025 A6 (Lemmon)", dt=dt)
        c2025_a6_lemmon.populate_constellation_id()

        assert c2025_a6_lemmon.name == "C/2025 A6 (Lemmon)"
        assert c2025_a6_lemmon.ra == 218.8720302905781
        assert c2025_a6_lemmon.dec == 27.73131019077249
        assert c2025_a6_lemmon.constellation_id == "boo"
        assert c2025_a6_lemmon.distance == 0.5980228047821197

    def test_comet_get_at_date_location(self):
        dt = datetime(2025, 10, 21, 19, 0, tzinfo=TZ_PT)
        lat = 33.363484
        lon = -116.836394

        c2025_a6_lemmon = Comet.get(name="C/2025 A6 (Lemmon)", dt=dt, lat=lat, lon=lon)
        c2025_a6_lemmon.populate_constellation_id()

        assert c2025_a6_lemmon.name == "C/2025 A6 (Lemmon)"
        assert c2025_a6_lemmon.constellation_id == "boo"

        # specifying location gets apparent location in the sky, so RA/DEC should be different
        assert c2025_a6_lemmon.ra == 218.86217824786402
        assert c2025_a6_lemmon.dec == 27.731583564862603

        # and distance should be different too
        assert c2025_a6_lemmon.distance == 0.5980091198158166

    def test_comet_get_trajectory(self):
        dt = datetime(2025, 10, 21, 19, 0, tzinfo=TZ_PT)
        lat = 33.363484
        lon = -116.836394

        c2025_a6_lemmon = Comet.get(name="C/2025 A6 (Lemmon)", dt=dt, lat=lat, lon=lon)

        dt_start = datetime(2025, 10, 19, 19, 0, tzinfo=TZ_PT)
        dt_end = datetime(2025, 11, 4, 19, 0, tzinfo=TZ_PT)

        comets = [
            c for c in c2025_a6_lemmon.trajectory(date_start=dt_start, date_end=dt_end)
        ]

        assert len(comets) == 16
        assert comets[0].dt == dt_start

        # last comet should be one day before end date because end is not inclusive
        assert comets[-1].dt == dt_end - timedelta(days=1)
