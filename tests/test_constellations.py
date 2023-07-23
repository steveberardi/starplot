from starplot.data import constellations


def test_constellation_label_count():
    assert len(constellations.properties.keys()) == 88
