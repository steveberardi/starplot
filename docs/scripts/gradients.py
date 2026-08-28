"""
Renders every built-in gradient available in Starplot: a small standalone
swatch for each one (via the same create_gradient() helper used to render
axes backgrounds), plus one example plot showing a gradient actually in use.
"""

from pathlib import Path

from starplot import MapPlot, StereoNorth, _, Constellation
from starplot.styles import PlotStyle, extensions, gradients
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

# Example: a custom-defined gradient (matching the styling/gradients.md
# example) applied to a real plot's axes background.
my_gradient = [
    (0.0, "#f4d58d"),
    (0.3, "#c17ecb"),
    (0.7, "#4b3f8f"),
    (1.0, "#100d29"),
]

example_style = PlotStyle().extend(
    extensions.BLUE_NIGHT,
    extensions.MAP,
)
example_style.axes.background.fill = my_gradient

cas = Constellation.get(iau_id="cas")

p = MapPlot(
    projection=StereoNorth(center_ra=15),
    ra_min=-5,
    ra_max=35,
    dec_min=55,
    dec_max=65,
    style=example_style,
    scale=1.5,
)
p.stars(
    where=[_.hip.isin(cas.star_hip_ids)],
    where_labels=False,
    style__marker__symbol="star_4",
    style__marker__stroke_width=4,
    size_fn=lambda s: 80,
)
p.constellations()
p.export(str(OUTPUT_DIR / "gradient_example.svg"))
