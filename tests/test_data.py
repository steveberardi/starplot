import importlib

from starplot import data


def test_download_path(monkeypatch):
    monkeypatch.setenv("STARPLOT_DOWNLOAD_PATH", "/testing")

    importlib.reload(data)

    assert data.DataFiles._DOWNLOAD_PATH.value == "/testing"
    assert data.DataFiles.BIG_SKY.value.startswith("/testing")
