import importlib
import os
from unittest import mock

from starplot import data

from .utils import TEST_DATA_PATH

# `starplot.settings` is the settings object, so the module must be imported by name
settings_module = importlib.import_module("starplot.settings")

data_path = str(TEST_DATA_PATH)


@mock.patch.dict(os.environ, {"STARPLOT_DATA_PATH": data_path})
def test_data_path():
    importlib.reload(settings_module)  # must reload this first
    importlib.reload(data)

    assert os.environ.get("STARPLOT_DATA_PATH") == data_path
    assert str(settings_module.settings.data_path) == data_path
