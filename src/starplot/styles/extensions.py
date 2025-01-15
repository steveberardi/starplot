from pathlib import Path

import yaml


HERE = Path(__file__).resolve().parent
EXT_PATH = HERE / "ext"


def load(filename: str) -> dict:
    with open(EXT_PATH / filename, "r") as infile:
        return yaml.safe_load(infile)


# Plot Types
OPTIC = load("optic.yml")
MAP = load("map.yml")

# Color Schemes
GRAYSCALE = load("grayscale.yml")
GRAYSCALE_DARK = load("grayscale_dark.yml")
BLUE_LIGHT = load("blue_light.yml")
BLUE_MEDIUM = load("blue_medium.yml")
BLUE_DARK = load("blue_dark.yml")
BLUE_GOLD = load("blue_gold.yml")
ANTIQUE = load("antique.yml")
NORD = load("nord.yml")
CB_WONG = load("cb_wong.yml")
COLOR_PRINT = load("color_print.yml")
