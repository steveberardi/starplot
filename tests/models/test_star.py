from shapely import Point

from starplot import DSO, Star, _


class TestStar:
    def test_star_get(self):
        sirius = Star.get(name="Sirius")
        constellation = sirius.constellation()

        assert sirius.magnitude == -1.44
        assert sirius.hip == 32349
        assert sirius.constellation_id == "cma"

        assert constellation.iau_id == "cma"
        assert constellation.name == "Canis Major"

    def test_star_get_sql(self):
        vega = Star.get(sql="select * from _ where name='Vega'")
        assert vega.magnitude == 0.03
        assert str(vega.hip) == "91262"
        assert str(vega.flamsteed) == "3"
        assert vega.constellation_id == "lyr"

    def test_star_get_returns_none_on_no_matches(self):
        assert Star.get(constellation_id="helloooo") is None

    def test_star_find(self):
        names = {"Sirius", "Bellatrix", "Castor", "Vega"}
        bright = Star.find(where=[_.name.isin(names)])
        assert len(bright) == 5  # Castor has two component stars in Big Sky catalog
        assert {s.name for s in bright} == names

    def test_star_find_sql(self):
        bright_stars = Star.find(sql="select * from _ where magnitude < 3")
        assert len(bright_stars) == 196

    def test_star_find_intersects(self):
        m45 = DSO.get(m="45")
        m45_stars = Star.find(
            where=[_.geometry.intersects(m45.geometry), _.magnitude < 8]
        )

        for star in m45_stars:
            assert star.geometry.intersects(m45.geometry)

    def test_star_is_primary_handles_int(self):
        s = Star(ra=1, dec=1, pk=1, geometry=Point(1, 1), ccdm=1, magnitude=2)
        assert s.is_primary
