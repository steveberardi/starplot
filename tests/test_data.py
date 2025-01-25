import importlib
import os

from unittest import mock
from starplot import data, settings


@mock.patch.dict(os.environ, {"STARPLOT_DOWNLOAD_PATH": "/testing"})
def test_download_path():
    importlib.reload(settings)  # must reload this first
    importlib.reload(data)

    assert os.environ.get("STARPLOT_DOWNLOAD_PATH") == "/testing"
    assert str(settings.DOWNLOAD_PATH) == "/testing"
    assert str(data.DataFiles.BIG_SKY).startswith("/testing")
