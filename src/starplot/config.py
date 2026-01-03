import os

from enum import Enum
from pathlib import Path
from dataclasses import dataclass, field


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
    data_path: Path = field(default_factory=_get_path("STARPLOT_DATA_PATH", Path.cwd()))
    """
    Path that Starplot will use for data and the DuckDB spatial extension, which is required for the data backend.
    
    Default = current working directory
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

    language: str = field(
        default_factory=lambda: os.environ.get("STARPLOT_LANGUAGE", "en-US")
    )
    """
    Default language for plotted labels, as an ISO-639 code. Case insensitive.

    Supported values:

    - `en-us` = English (default)
    - `fa` = Persian (Farsi). Make sure you have a Persian font installed that supports RTL (such as [Vazir](https://github.com/rastikerdar/vazir-font) or [Noto Sans Arabic](https://fonts.google.com/noto/specimen/Noto+Sans+Arabic)) and set it as the font in your plot's style.
    - `fr` = French
    - `lt` = Lithuanian
    - `zh-cn` = Chinese. Make sure you have a good Chinese font installed (such as [Noto Sans SC](https://fonts.google.com/noto/specimen/Noto+Sans+SC)) and you'll also need to set that as the font in your plot's style.
    - `zh-tw` = Traditional Chinese

    **🌐 Want to see another language available? Please help us add it! [Details here](https://github.com/steveberardi/starplot/tree/main/data/raw/translations).**
    """


settings = Settings()
