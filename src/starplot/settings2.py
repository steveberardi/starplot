import os

from enum import Enum
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


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


class SvgTextType(str, Enum):
    PATH = "path"
    ELEMENT = "element"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="STARPLOT_")

    download_path: Path = str(DATA_PATH / "downloads")
    """Path for downloaded data"""

    duckdb_extension_path: Path = str(DATA_PATH / "duckdb-extensions")
    """Path for DuckDB extensions"""

    svg_text_type: SvgTextType = SvgTextType.PATH
    """
    Method for rendering text in SVG exports:

    - "path" (default) will render all text as paths. This will increase the filesize, but allow all viewers to see the font correctly (even if they don't have the font installed on their system).

    - "element" will render all text as an SVG `<text>` element, which means the text will be editable in graphic design applications but the text may render in a system default font if the original font isn't available. **Important: when using the "element" method, text borders will be turned OFF.**
    
    """

    message: str = "hello"


config = Settings()
