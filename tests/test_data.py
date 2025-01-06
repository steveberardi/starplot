import importlib

from starplot import data


def test_download_path(monkeypatch):
    monkeypatch.setenv("STARPLOT_DOWNLOAD_PATH", "/testing")

    importlib.reload(data)

    assert str(data.DOWNLOAD_PATH) == "/testing"
    assert str(data.DataFiles.BIG_SKY).startswith("/testing")
