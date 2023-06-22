from starplot.constellations import labels


def test_constellation_label_count():
    assert len(labels.keys()) == 88
