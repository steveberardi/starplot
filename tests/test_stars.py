from starplot.stars import hip_names


def test_star_hip_names():
    assert hip_names[95947] == "Albireo"
    assert hip_names[11767] == "Polaris"
    assert hip_names[32349] == "Sirius"
    assert hip_names[91262] == "Vega"
