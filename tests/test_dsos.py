from starplot.data import dsos


def test_messier():
    assert len(dsos.messier) == 109


def test_dso_base():
    assert "M42" in dsos.ZENITH_BASE
    assert "M13" in dsos.ZENITH_BASE
