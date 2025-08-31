from enum import Enum
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


STARPLOT_PATH = Path(__file__).resolve().parent
"""Path of starplot source"""

DATA_PATH = STARPLOT_PATH / "data" / "library"
"""Path of starplot data"""


RAW_DATA_PATH = STARPLOT_PATH.parent.parent / "raw"
BUILD_PATH = STARPLOT_PATH.parent.parent / "build"


class SvgTextType(str, Enum):
    PATH = "path"
    ELEMENT = "element"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="STARPLOT_")
    """Configuration for the Pydantic settings model. Do not change."""

    download_path: Path = DATA_PATH / "downloads"
    """
    Path for downloaded data, including the Big Sky catalog, ephemeris files, etc.
    
    Default = `<starplot_source_path>/data/library/downloads/`
    """

    duckdb_extension_path: Path = DATA_PATH / "duckdb-extensions"
    """
    Path for the DuckDB spatial extension, which is required for the data backend.

    Default = `<starplot_source_path>/data/library/duckdb-extensions/`
    """

    svg_text_type: SvgTextType = SvgTextType.PATH
    """
    Method for rendering text in SVG exports:

    - `"path"` (default) will render all text as paths. This will increase the filesize, 
    but allow all viewers to see the font correctly (even if they don't have the font 
    installed on their system).

    - `"element"` will render all text as an [SVG `<text>` element](https://developer.mozilla.org/en-US/docs/Web/SVG/Reference/Element/text), 
    which means the text will be editable in graphic design applications but the text may render in a system default font if the original 
    font isn't available. **Important: when using the "element" method, text borders will be turned OFF.**
    
    """


settings = Settings()
