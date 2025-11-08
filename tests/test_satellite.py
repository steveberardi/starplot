import pytest

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from starplot import Satellite

TZ_PT = ZoneInfo("America/Los_Angeles")

ISS_JSON_22_OCT_2025 = {
    "OBJECT_NAME": "ISS (ZARYA)",
    "OBJECT_ID": "1998-067A",
    "EPOCH": "2025-10-22T00:11:31.403904",
    "MEAN_MOTION": 15.49333878,
    "ECCENTRICITY": 0.0004414,
    "INCLINATION": 51.6346,
    "RA_OF_ASC_NODE": 38.5904,
    "ARG_OF_PERICENTER": 322.0877,
    "MEAN_ANOMALY": 37.98,
    "EPHEMERIS_TYPE": 0,
    "CLASSIFICATION_TYPE": "U",
    "NORAD_CAT_ID": 25544,
    "ELEMENT_SET_NO": 999,
    "REV_AT_EPOCH": 53483,
    "BSTAR": 0.00027406,
    "MEAN_MOTION_DOT": 0.00014857,
    "MEAN_MOTION_DDOT": 0,
}


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
        assert dsp.ra == pytest.approx(18.22796127417007, rel=1e-9)
        assert dsp.dec == pytest.approx(-14.166679872233521, rel=1e-9)

    def test_satellite_from_json(self):
        iss = Satellite.from_json(
            data=ISS_JSON_22_OCT_2025,
            dt=datetime(2025, 10, 21, 19, 0, 0, 0, tzinfo=TZ_PT),
            lat=33.363484,
            lon=-116.836394,
        )
        assert iss.name == "ISS (ZARYA)"
        assert iss.ra == pytest.approx(105.27042780805024, rel=1e-9)
        assert iss.dec == pytest.approx(6.7511296688128315, rel=1e-9)

    def test_satellite_get_trajectory(self):
        iss = Satellite.from_json(
            data=ISS_JSON_22_OCT_2025,
            dt=datetime(2025, 10, 21, 19, 0, 0, 0, tzinfo=TZ_PT),
            lat=33.363484,
            lon=-116.836394,
        )

        dt_start = datetime(2025, 10, 19, 19, 0, tzinfo=TZ_PT)
        dt_end = datetime(2025, 10, 21, 19, 0, tzinfo=TZ_PT)

        satellites = [s for s in iss.trajectory(date_start=dt_start, date_end=dt_end)]

        # default time step for satellite trajectory is 1 hour
        assert len(satellites) == 48

        assert satellites[0].dt == dt_start

        # last satellite should be one hour before end time because end is not inclusive
        assert satellites[-1].dt == dt_end - timedelta(hours=1)
