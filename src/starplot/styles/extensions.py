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
    "axes": {"background": {"fill": {"stops": gradients.DAYLIGHT, "type": "linear"}}},
}

GRADIENT_BOLD_SUNSET = {
    "axes": {
        "background": {"fill": {"stops": gradients.BOLD_SUNSET, "type": "linear"}}
    },
}


GRADIENT_CIVIL_TWILIGHT = {
    "axes": {
        "background": {"fill": {"stops": gradients.CIVIL_TWILIGHT, "type": "linear"}}
    },
}

GRADIENT_NAUTICAL_TWILIGHT = {
    "axes": {
        "background": {"fill": {"stops": gradients.NAUTICAL_TWILIGHT, "type": "linear"}}
    },
}

GRADIENT_ASTRONOMICAL_TWILIGHT = {
    "axes": {
        "background": {
            "fill": {"stops": gradients.ASTRONOMICAL_TWILIGHT, "type": "linear"}
        }
    },
}

GRADIENT_TRUE_NIGHT = {
    "axes": {"background": {"fill": {"stops": gradients.TRUE_NIGHT, "type": "linear"}}},
}

GRADIENT_PRE_DAWN = {
    "axes": {"background": {"fill": {"stops": gradients.PRE_DAWN, "type": "linear"}}},
}

GRADIENT_OPTIC_FALLOFF = {
    "axes": {
        "background": {"fill": {"stops": gradients.OPTIC_FALLOFF, "type": "radial"}}
    },
}

# needs work
GRADIENT_OPTIC_FALL_IN = {
    "axes": {
        "background": {"fill": {"stops": gradients.OPTIC_FALL_IN, "type": "radial"}}
    },
}
