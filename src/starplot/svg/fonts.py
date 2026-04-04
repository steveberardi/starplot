import sys
import zipfile
from functools import cache
from pathlib import Path

from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen

from starplot.config import settings
from starplot.data.utils import download

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
    # TODO : handle font collections (.ttc) and variable fonts

    font = TTFont(font_path)
    os2 = font.get("OS/2")

    # record = font["name"].getName(1, 3, 1, 0x0409)
    # name = record.toUnicode() if record else None

    name = font["name"].getDebugName(16) or font["name"].getDebugName(1)

    if not name:
        return None

    weight = os2.usWeightClass if os2 else 400
    italic = bool(os2.fsSelection & 0x01) if os2 else False
    # bold = bool(os2.fsSelection & 0x20) if os2 else False

    return name.lower(), weight, italic


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


@cache
def find_font(family: str, weight: int, italic: bool) -> TTFont:
    font_index = build_font_index()
    font_path = font_index.get((family.lower(), weight, italic))

    if not font_path:
        font_path = font_index.get((family.lower(), 400, italic))
    font = TTFont(font_path)

    # glyf = font.getGlyphSet()
    # cmap = font.getBestCmap()

    # units_per_em = font["head"].unitsPerEm

    # return glyf, cmap, units_per_em
    return font


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


def download_fonts():
    FONTS_PATH.mkdir(parents=True, exist_ok=True)

    fonts = {
        "inter": {
            "url": "https://github.com/rsms/inter/releases/download/v4.1/Inter-4.1.zip",
            "extract_files": [
                "extras/ttf/Inter-Regular.ttf",
                "extras/ttf/Inter-Thin.ttf",
                "extras/ttf/Inter-Light.ttf",
                "extras/ttf/Inter-ExtraLight.ttf",
                "extras/ttf/Inter-Medium.ttf",
                "extras/ttf/Inter-Italic.ttf",
                "extras/ttf/Inter-ThinItalic.ttf",
                "extras/ttf/Inter-LightItalic.ttf",
                "extras/ttf/Inter-ExtraLightItalic.ttf",
                "extras/ttf/Inter-MediumItalic.ttf",
                "extras/ttf/Inter-SemiBoldItalic.ttf",
                "extras/ttf/Inter-BoldItalic.ttf",
                "extras/ttf/Inter-ExtraBoldItalic.ttf",
                "extras/ttf/Inter-BlackItalic.ttf",
                "extras/ttf/Inter-Bold.ttf",
                "extras/ttf/Inter-SemiBold.ttf",
                "extras/ttf/Inter-ExtraBold.ttf",
                "extras/ttf/Inter-Black.ttf",
            ],
        },
        "gfs-didot": {
            "url": "https://github.com/google/fonts/raw/refs/heads/main/ofl/gfsdidot/GFSDidot-Regular.ttf",
            "extract_files": None,
        },
    }

    for font, props in fonts.items():
        path = FONTS_PATH / font
        path.mkdir(parents=True, exist_ok=True)

        download_path = path / props["url"].split("/")[-1]
        download(
            url=props["url"], download_path=download_path, description=f"Font ({font})"
        )

        extract_files = props.get("extract_files")

        if extract_files:
            with zipfile.ZipFile(download_path) as zf:
                for member in extract_files:
                    zf.extract(member, path)
