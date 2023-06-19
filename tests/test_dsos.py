from starplot.dsos import messier, DSO_BASE


def test_messier():
    assert len(messier) == 109

def test_dso_base():
    assert "M42" in DSO_BASE
    assert "M13" in DSO_BASE
