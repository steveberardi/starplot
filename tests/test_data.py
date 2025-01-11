import importlib




def test_download_path(monkeypatch):
    monkeypatch.setenv("STARPLOT_DOWNLOAD_PATH", "/testing")

    # importlib.reload(data)
    # importlib.reload(settings)
    from starplot import data, settings

    assert str(settings.DOWNLOAD_PATH) == "/testing"
    assert str(data.DataFiles.BIG_SKY).startswith("/testing")
