import sys
from functools import cache
from pathlib import Path

from fontTools.ttLib import TTFont

from starplot.config import settings

FONTS_PATH = settings.data_path / "fonts"

def get_font_paths() -> list[Path]:
    paths = []

    if sys.platform == "win32":
        paths = [
            Path(r"C:\Windows\Fonts"),
            Path.home() / "AppData" / "Local" / "Microsoft" / "Windows" / "Fonts",
        ]
    elif sys.platform == "darwin":
        paths = [
            Path("/System/Library/Fonts"),
            Path("/Library/Fonts"),
            Path.home() / "Library" / "Fonts",
        ]
    else:  # Linux / BSD / etc
        paths = [
            Path("/usr/share/fonts"),
            Path("/usr/local/share/fonts"),
            Path.home() / ".fonts",
            Path.home() / ".local" / "share" / "fonts",
        ]
    
    paths.append(FONTS_PATH)

    return [p for p in paths if p.exists()]


def get_font_filenames(extensions: tuple[str] = (".ttf", ".otf")) -> list[Path]:

    fonts = []
    for d in get_font_paths():
        for ext in extensions:
            fonts.extend(d.rglob(f"*{ext}"))
    return fonts


def get_font_info(font_path: str) -> dict:
    # TODO : handle font collections (.ttc)

    font = TTFont(font_path)
    os2 = font.get("OS/2")

    record = font["name"].getName(1, 3, 1, 0x0409)
    name = record.toUnicode() if record else None

    if not name:
        return None

    weight = os2.usWeightClass if os2 else 400
    italic = bool(os2.fsSelection & 0x01) if os2 else False
    bold = bool(os2.fsSelection & 0x20) if os2 else False

    return name.lower(), weight, italic, bold

@cache
def build_font_index() -> dict:
    """
    Returns dictionary that maps font properties to their filename.

    Each key is a tuple of properties:

    (family, weight, italic, bold) = font_path
    """
    result = {}
    for font_path in get_font_filenames():
        key = get_font_info(font_path)
        if key:
            result[key] = font_path
    
    return result



def text_to_svg_path(
    text: str,
    font_path: str,
    font_size: float = 48,
    x: float = 0,
    y: float = 0,
) -> str:
    font = TTFont(font_path)
    glyf = font.getGlyphSet()
    cmap = font.getBestCmap()

    print(font["OS/2"].usWeightClass)

    units_per_em = font["head"].unitsPerEm
    scale = font_size / units_per_em

    paths = []
    cursor_x = x

    for char in text:
        codepoint = ord(char)
        glyph_name = cmap.get(codepoint)
        if not glyph_name:
            continue

        glyph = glyf[glyph_name]
        pen = SVGPathPen(glyf)
        glyph.draw(pen)

        if pen.getCommands():
            # SVG y-axis is flipped vs font coordinates
            paths.append(
                f'<path transform="translate({cursor_x},{y}) scale({scale},{-scale})" d="{pen.getCommands()}" />'
            )

        advance = glyph.width * scale
        cursor_x += advance

    return "\n".join(paths)
