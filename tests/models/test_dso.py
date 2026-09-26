from starplot import DSO, _


class TestDSO:
    def test_dso_get(self):
        m13 = DSO.get(m="13")
        assert m13.ra == 250.4235
        assert m13.dec == 36.4613
        assert m13.m == "13"
        assert m13.ngc == "6205"
        assert m13.ic is None
        assert m13.constellation_id == "her"

        m44 = DSO.get(sql="select * from _ where m='44'")
        assert m44.m == "44"
        assert m44.constellation_id == "cnc"

    def test_dso_find_messier(self):
        results = DSO.find(where=[_.m.notnull()])
        assert len(results) == 110

        sql_results = DSO.find(sql="select * from _ where m is not null")
        assert len(sql_results) == 110

    def test_dso_find_duplicate(self):
        results = DSO.find(where=[_.ngc == "5273"])
        assert len(results) == 2

        for r in results:
            assert r.m is None
            assert r.ngc == "5273"
            assert r.ic == "895"
