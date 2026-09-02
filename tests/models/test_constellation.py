from starplot import Constellation, _


class TestConstellation:
    def test_constellation_get(self):
        hercules = Constellation.get(iau_id="her")
        assert hercules.name == "Hercules"
        assert hercules.ra == 253.2
        assert hercules.dec == 34.86

        draco = Constellation.get(sql="select * from _ where iau_id='dra'")
        assert draco.name == "Draco"

    def test_constellation_find(self):
        results = Constellation.find(
            where=[_.name.isin(["Canis Major", "Andromeda", "Orion"])]
        )
        assert len(results) == 3

        sql_results = Constellation.find(sql="select * from _ where name = 'Lyra'")
        assert len(sql_results) == 1
        assert sql_results[0].iau_id == "lyr"
