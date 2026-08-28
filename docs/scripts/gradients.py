"""
Renders every built-in gradient available in Starplot: a small standalone
swatch for each one (via the same create_gradient() helper used to render
axes backgrounds), plus one example plot showing a gradient actually in use.
"""

from pathlib import Path

from starplot.styles import gradients
from starplot.styles.constants import GradientType
from starplot.svg.elements import SVG, Defs, Rectangle, create_gradient

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "images" / "reference"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

SWATCH_WIDTH = 1200
SWATCH_HEIGHT = 800

GRADIENT_NAMES = [
    "daylight",
    "sun",
    "new_moon",
    "bold_sunset",
    "civil_twilight",
    "nautical_twilight",
    "astronomical_twilight",
    "true_night",
    "pre_dawn",
    "optic_falloff",
    "optic_fall_in",
]

for name in GRADIENT_NAMES:
    stops = getattr(gradients, name.upper())
    gradient = create_gradient(stops=stops, type=GradientType.LINEAR, id=f"g-{name}")
    swatch = SVG(
        height=SWATCH_HEIGHT,
        width=SWATCH_WIDTH,
        children=[
            Defs(children=[gradient]),
            Rectangle(
                x=0,
                y=0,
                height=SWATCH_HEIGHT,
                width=SWATCH_WIDTH,
                attrs={"fill": gradient.url},
            ),
        ],
    )
    (OUTPUT_DIR / f"gradient_{name}.svg").write_text(swatch.render())
