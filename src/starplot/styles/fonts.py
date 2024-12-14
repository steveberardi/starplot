from pathlib import Path

from matplotlib import font_manager

HERE = Path(__file__).resolve().parent
FONTS_PATH = HERE / "fonts-library"


def load():
    """Loads all fonts in ./fonts-library"""
    font_dirs = [FONTS_PATH]
    font_files = font_manager.findSystemFonts(fontpaths=font_dirs)

    for font_file in font_files:
        font_manager.fontManager.addfont(font_file)
