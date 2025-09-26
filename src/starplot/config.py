import os
from enum import Enum
from pathlib import Path
from dataclasses import dataclass, field


STARPLOT_PATH = Path(__file__).resolve().parent
"""Path of starplot source"""

DATA_PATH = STARPLOT_PATH / "data" / "library"
"""Path of starplot data"""


RAW_DATA_PATH = STARPLOT_PATH.parent.parent / "raw"
BUILD_PATH = STARPLOT_PATH.parent.parent / "build"


def _get_path(var_name, default) -> Path:
    def _get():
        value = os.environ.get(var_name, default)
        return Path(value)

    return _get


class SvgTextType(str, Enum):
    PATH = "path"
    ELEMENT = "element"


@dataclass
class Settings:
    download_path: Path = field(
        default_factory=_get_path("STARPLOT_DOWNLOAD_PATH", DATA_PATH / "downloads")
    )
    """
    Path for downloaded data, including the Big Sky catalog, ephemeris files, etc.
    
    Default = `<starplot_source_path>/data/library/downloads/`
    """

    duckdb_extension_path: Path = field(
        default_factory=_get_path(
            "STARPLOT_DUCKDB_EXTENSION_PATH", DATA_PATH / "duckdb-extensions"
        )
    )
    """
    Path for the DuckDB spatial extension, which is required for the data backend.

    Default = `<starplot_source_path>/data/library/duckdb-extensions/`
    """

    svg_text_type: SvgTextType = field(
        default_factory=lambda: os.environ.get(
            "STARPLOT_SVG_TEXT_TYPE", SvgTextType.PATH
        )
    )
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
