"""
Generates an HTML reference page with one card per map projection: its name,
description, constructor properties, and a preview image (gridlines + Tissot
indicatrix, rendered separately by docs/scripts/projections.py). The page's
HTML/CSS lives in the Jinja2 template projection_list.html, next to this
file; this module only extracts and shapes the data.

Field/doc extraction reuses the same AST-based approach as style_explorer.py,
so this doesn't need to import starplot (or its heavier dependencies like
pyproj/skyfield) just to read class docstrings and field defaults.

This code was created via Claude Code.
"""

import ast
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
PROJECTIONS_FILE = REPO_ROOT / "src" / "starplot" / "projections.py"
SCRIPT_DIR = Path(__file__).resolve().parent
OUTPUT_PATH = REPO_ROOT / "docs" / "images" / "reference" / "projection_list.html"

# Each projection shown, in the order they should appear, paired with the
# SVG filename slug used by docs/scripts/projections.py (e.g. StereoNorth's
# preview image is docs/images/reference/projection_stereo_north.svg).
# AutoProjection is deliberately excluded -- it exposes no public
# properties (see its own docstring) and isn't a MapPlot projection choice
# so much as an automatic fallback among the ones listed here.
PROJECTIONS = [
    ("Equidistant", "equidistant"),
    ("LambertAzEqArea", "lambert_az_eq_area"),
    ("Mercator", "mercator"),
    ("Miller", "miller"),
    ("Mollweide", "mollweide"),
    ("ObliqueMercator", "oblique_mercator"),
    ("Orthographic", "orthographic"),
    ("PlateCarree", "plate_carree"),
    ("Robinson", "robinson"),
    ("StereoNorth", "stereo_north"),
    ("StereoSouth", "stereo_south"),
    ("Stereographic", "stereographic"),
    ("Gnomonic", "gnomonic"),
]

# The only base classes in projections.py that expose user-facing
# constructor properties -- ProjectionBase itself carries several
# internal/implementation fields (proj_def_base, global_only, curved,
# wraps, r, units, ...) that aren't meant to be set by users, so those are
# deliberately not walked at all.
BASE_PROPERTIES = {
    "CenterRA": ["center_ra"],
    "CenterDEC": ["center_dec"],
    "CenterRADEC": ["center_ra", "center_dec"],
    "Azimuth": ["azimuth"],
}
PROPERTY_ORDER = ["center_ra", "center_dec", "azimuth"]

PROJ_DOCS_URL = "https://proj.org/en/stable/operations/projections/{}.html"


def _unparse(node):
    return None if node is None else ast.unparse(node)


def _first_paragraph(doc):
    if not doc:
        return ""
    return " ".join(doc.strip().split("\n\n")[0].split())


def extract_classes(path: Path) -> dict:
    """Parses projections.py and returns {class_name: {bases, doc, fields}}."""
    tree = ast.parse(path.read_text())
    classes = {}

    for node in tree.body:
        if not isinstance(node, ast.ClassDef):
            continue

        fields = []
        for stmt in node.body:
            if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
                value = None
                if isinstance(stmt.value, ast.Constant):
                    value = stmt.value.value
                fields.append({"name": stmt.target.id, "value": value})

        classes[node.name] = {
            "bases": [_unparse(b) for b in node.bases],
            "doc": _first_paragraph(ast.get_docstring(node) or ""),
            "fields": fields,
        }

    return classes


def resolve_properties(class_name: str, classes: dict) -> list[str]:
    """Which of center_ra/center_dec/azimuth a projection class exposes,
    via its CenterRA/CenterDEC/CenterRADEC/Azimuth bases, plus any of
    those names it overrides directly in its own body (e.g. StereoNorth
    fixes center_dec to 90 while only inheriting CenterRA)."""
    names = set()
    for base in classes[class_name]["bases"]:
        names.update(BASE_PROPERTIES.get(base, []))

    own_names = {f["name"] for f in classes[class_name]["fields"]}
    names.update(own_names & set(PROPERTY_ORDER))

    return [name for name in PROPERTY_ORDER if name in names]


def proj_operation_name(class_name: str, classes: dict) -> str:
    """The proj4 operation code each projection class sets as its own
    `name` ClassVar (e.g. ObliqueMercator's is "omerc") -- this is the
    same string the class passes as `proj` when building its CRS (see
    ProjectionBase.get_crs), and it's also the filename PROJ's own docs
    use for that operation's page."""
    for field in classes[class_name]["fields"]:
        if field["name"] == "name":
            return field["value"]
    raise ValueError(f"{class_name} has no `name` ClassVar")


def build_cards(classes: dict) -> list[dict]:
    cards = []
    for class_name, slug in PROJECTIONS:
        cdef = classes[class_name]
        proj_name = proj_operation_name(class_name, classes)
        cards.append(
            {
                "name": class_name,
                "doc": cdef["doc"],
                "properties": resolve_properties(class_name, classes),
                "image": f"projection_{slug}.svg",
                "proj_url": PROJ_DOCS_URL.format(proj_name),
            }
        )
    return cards


def build_html(cards: list[dict]) -> str:
    env = Environment(
        loader=FileSystemLoader(SCRIPT_DIR),
        autoescape=select_autoescape(["html", "jinja"]),
    )
    template = env.get_template("projection_list.html")
    return template.render(cards=cards)


def main():
    classes = extract_classes(PROJECTIONS_FILE)
    cards = build_cards(classes)
    html = build_html(cards)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(html)
    print(f"Wrote {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
