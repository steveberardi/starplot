import importlib
import os

from unittest import mock
from starplot import data, config


@mock.patch.dict(os.environ, {"STARPLOT_DATA_PATH": "/testing"})
def test_download_path():
    importlib.reload(config)  # must reload this first
    importlib.reload(data)

    assert os.environ.get("STARPLOT_DATA_PATH") == "/testing"
    assert str(config.settings.data_path) == "/testing"
