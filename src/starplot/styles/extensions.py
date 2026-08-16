from pathlib import Path

import yaml

from starplot.styles import gradients

HERE = Path(__file__).resolve().parent
EXT_PATH = HERE / "ext"


def load(filename: str) -> dict:
    with open(EXT_PATH / filename, "r") as infile:
        return yaml.safe_load(infile)


# Plot Types
OPTIC = load("optic.yml")
MAP = load("map.yml")
HORIZON = load("horizon.yml")

# Color Themes
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
PUBLICATION = load("publication.yml")
STARPLOT = load("starplot.yml")

FIGURE_TRANSPARENT = {
    "figure": {"background": {"fill": None}},
}

GRADIENT_DAYLIGHT = {
    "axes": {"background": {"fill": gradients.DAYLIGHT}},
}

GRADIENT_BOLD_SUNSET = {
    "axes": {"background": {"fill": gradients.BOLD_SUNSET}},
}


GRADIENT_CIVIL_TWILIGHT = {
    "axes": {"background": {"fill": gradients.CIVIL_TWILIGHT}},
}

GRADIENT_NAUTICAL_TWILIGHT = {
    "axes": {"background": {"fill": gradients.NAUTICAL_TWILIGHT}},
}

GRADIENT_ASTRONOMICAL_TWILIGHT = {
    "axes": {"background": {"fill": gradients.ASTRONOMICAL_TWILIGHT}},
}

GRADIENT_TRUE_NIGHT = {
    "axes": {"background": {"fill": gradients.TRUE_NIGHT}},
}

GRADIENT_PRE_DAWN = {
    "axes": {"background": {"fill": gradients.PRE_DAWN}},
}

GRADIENT_OPTIC_FALLOFF = {
    "axes": {"background": {"fill": gradients.OPTIC_FALLOFF}},
}

# needs work
GRADIENT_OPTIC_FALL_IN = {
    "axes": {"background": {"fill": gradients.OPTIC_FALL_IN}},
}
