import os

from pathlib import Path


def env(name, default):
    return os.environ.get(name) or default


STARPLOT_PATH = Path(__file__).resolve().parent
"""Path of starplot source"""

DATA_PATH = STARPLOT_PATH / "data" / "library"
"""Path of starplot data"""

DOWNLOAD_PATH = Path(env("STARPLOT_DOWNLOAD_PATH", str(DATA_PATH / "downloads")))
"""Path for downloaded data"""

DUCKDB_EXTENSION_PATH = Path(
    env("STARPLOT_DUCKDB_EXTENSIONS_PATH", str(DATA_PATH / "duckdb-extensions"))
)
"""Path for DuckDB extensions"""


RAW_DATA_PATH = STARPLOT_PATH.parent.parent / "raw"
BUILD_PATH = STARPLOT_PATH.parent.parent / "build"
