import importlib
import os
from unittest import mock

from starplot import config, data

from .utils import TEST_DATA_PATH

data_path = str(TEST_DATA_PATH)


@mock.patch.dict(os.environ, {"STARPLOT_DATA_PATH": data_path})
def test_data_path():
    importlib.reload(config)  # must reload this first
    importlib.reload(data)

    assert os.environ.get("STARPLOT_DATA_PATH") == data_path
    assert str(config.settings.data_path) == data_path
