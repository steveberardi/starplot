import importlib

from starplot import data


def test_download_path(monkeypatch):
    monkeypatch.setenv("STARPLOT_DOWNLOAD_PATH", "/testing")

    importlib.reload(data)

    assert data.DOWNLOAD_PATH == "/testing"
    assert data.DataFiles.BIG_SKY.startswith("/testing")
