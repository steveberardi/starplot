import importlib
import os

import pytest


@pytest.fixture
def temp_data_path(tmp_path):
    """
    Points STARPLOT_DATA_PATH at a temp directory for the duration of the
    test. Several modules bake `settings.data_path` into module-level
    objects at import time (e.g. each Catalog's own `.path`), so those
    modules are reloaded to pick up the temp path -- and reloaded again
    afterward to restore the real (already-downloaded) data path for
    whatever test runs next. Without this, catalogs that already exist on
    disk here would make `download_if_not_exists()` skip calling download().
    """
    from starplot import cli, config, data
    from starplot.data import catalogs
    from starplot.svg import fonts

    modules = [config, data, catalogs, fonts, cli]
    original = os.environ.get("STARPLOT_DATA_PATH")
    os.environ["STARPLOT_DATA_PATH"] = str(tmp_path)
    for module in modules:
        importlib.reload(module)

    try:
        yield tmp_path
    finally:
        if original is None:
            os.environ.pop("STARPLOT_DATA_PATH", None)
        else:
            os.environ["STARPLOT_DATA_PATH"] = original
        for module in modules:
            importlib.reload(module)
