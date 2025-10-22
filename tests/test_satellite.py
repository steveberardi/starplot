from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from starplot import Satellite

TZ_PT = ZoneInfo("America/Los_Angeles")


class TestSatellite:
    def test_satellite_from_tle(self):
        dsp = Satellite.from_tle(
            name="DSP",
            line1="1 04630U 70093A   25292.65131557 -.00000140  00000+0  00000+0 0  9999",
            line2="2 04630  14.7699  40.6283 1365231 267.2558  75.6583  1.20217148240949",
            dt=datetime(2025, 10, 21, 19, 0, 0, 0, tzinfo=TZ_PT),
            lat=33.363484,
            lon=-116.836394,
        )

        assert dsp.name == "DSP"
        assert dsp.ra == 18.22796127417007
        assert dsp.dec == -14.166679872233521

    # def test_comet_get_trajectory(self):
    #     dt = datetime(2025, 10, 21, 19, 0, tzinfo=TZ_PT)
    #     lat = 33.363484
    #     lon = -116.836394

    #     c2025_a6_lemmon = Comet.get(name="C/2025 A6 (Lemmon)", dt=dt, lat=lat, lon=lon)

    #     dt_start = datetime(2025, 10, 19, 19, 0, tzinfo=TZ_PT)
    #     dt_end = datetime(2025, 11, 4, 19, 0, tzinfo=TZ_PT)

    #     comets = [
    #         c for c in c2025_a6_lemmon.trajectory(date_start=dt_start, date_end=dt_end)
    #     ]

    #     assert len(comets) == 16
    #     assert comets[0].dt == dt_start

    #     # last comet should be one day before end date because end is not inclusive
    #     assert comets[-1].dt == dt_end - timedelta(days=1)
