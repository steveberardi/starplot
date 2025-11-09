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
BLUE_NIGHT = load("blue_night.yml")
ANTIQUE = load("antique.yml")
NORD = load("nord.yml")
CB_WONG = load("cb_wong.yml")
COLOR_PRINT = load("color_print.yml")

# Horizon Background Gradient Presets
# GRADIENTS = load("gradient_presets.yml")

GRADIENT_DAYLIGHT = {
    "background_color": [
        (0.0, "#7abfff"),
        (0.1, "#7abfff"),
        (0.9, "#568feb"),
        (0.9, "#3f7ee3"),
    ]
}

GRADIENT_BOLD_SUNSET = {
    "background_color": [
        [0.0, "#FFAF36"],
        [0.1, "#F56140"],
        [0.25, "#932885"],
        [0.4, "#591D76"],
        [0.7, "#0B0C40"],
        [1.0, "#000033"],
    ]
}


GRADIENT_CIVIL_TWILIGHT = {
    "background_color": [
        [0.0, "#F6C9A1"],
        [0.1, "#DCD4BB"],
        [0.3, "#96C6D6"],
        [0.55, "#4199CF"],
        [1.0, "#3A73A1"],
    ]
}

GRADIENT_NAUTICAL_TWILIGHT = {
    "background_color": [
        [0.0, "#F3C176"],
        [0.1, "#9292C9"],
        [0.25, "#4661D6"],
        [0.4, "#5428B2"],
        [0.7, "#2C105F"],
        [1.0, "#14012C"],
    ]
}

GRADIENT_ASTRONOMICAL_TWILIGHT = {
    "background_color": [
        [0.0, "#00184C"],
        [0.1, "#001B42"],
        [0.4, "#000D37"],
        [0.7, "#00061D"],
        [1.0, "#000000"],
    ]
}

GRADIENT_TRUE_NIGHT = {
    "background_color": [
        [0.0, "#00002B"],
        [0.1, "#00002B"],
        [0.3, "#000022"],
        [0.7, "#000018"],
        [1.0, "#000000"],
    ]
}

GRADIENT_PRE_DAWN = {
    "background_color": [
        [0.0, "#FEDCAF"],
        [0.05, "#BEB0D0"],
        [0.15, "#8274C9"],
        [0.3, "#444294"],
        [0.45, "#222164"],
        [0.7, "#000033"],
        [1.0, "#000000"],
    ]
}

GRADIENT_OPTIC_FALLOFF = {
    "background_color": [
        [0.0, "hsl(0, 0%, 0%)"],
        [0.1, "hsl(0, 0%, 8%)"],
        [0.3, "hsl(0, 0%, 12%)"],
        [0.6, "hsl(0, 0%, 14%)"],
        [1.0, "hsl(0, 0%, 20%)"],
    ]
}

# needs work
GRADIENT_OPTIC_FALL_IN = {
    "background_color": [
        [0.0, "hsl(0, 0%, 50%)"],
        [0.3, "hsl(0, 0%, 25%)"],
        [0.45, "hsl(0, 0%, 20%)"],
        [0.7, "hsl(0, 0%, 10%)"],
        [1.0, "hsl(0, 0%, 0%)"],
    ]
}
