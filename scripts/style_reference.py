"""
Generates an HTML reference page for every style property on PlotStyle,
as a single navigable tree: PlotStyle's own properties (star, gridlines,
axes, etc), each expanding in place to the fields of its style type, which
themselves expand in place for any nested style type (e.g. ObjectStyle's
`marker` field expands to MarkerStyle's fields), and so on down to plain
values.

Field names, types, defaults, and descriptions are all read directly from
the pydantic models in starplot/styles/plot.py and starplot/styles/elements.py
via the ast module, so the page can't drift from the actual source. Since
many properties share the same underlying style type (most DSOs, planets,
the moon, and the sun are all ObjectStyle, for example), that type's fields
get repeated at every place it's used -- deliberately, so each branch of
the tree is self-contained and expands right where it is instead of
jumping elsewhere on the page.

This module only extracts and shapes the data; the page's HTML, CSS, and
JS all live in the Jinja2 template style_reference.html, next to this file.
"""

import ast
import html as htmlmod
import re
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

REPO_ROOT = Path(__file__).resolve().parent.parent
STYLES_DIR = REPO_ROOT / "src" / "starplot" / "styles"
SCRIPT_DIR = Path(__file__).resolve().parent
OUTPUT_PATH = REPO_ROOT / "docs" / "snippets" / "style_reference.html"

# Groups of PlotStyle's own properties, in the order they should appear.
# This mirrors the section comments in styles/plot.py (# Stars, # Deep Sky
# Objects, etc) -- real structure from the source, not an invented one.
GROUPS = [
    ("Layout", ["axes", "figure", "title", "table", "legend"]),
    ("Stars", ["star", "bayer_labels", "flamsteed_labels"]),
    ("Solar System", ["planets", "moon", "sun"]),
    (
        "Deep Sky Objects",
        [
            "dso_open_cluster",
            "dso_association_stars",
            "dso_globular_cluster",
            "dso_galaxy",
            "dso_nebula",
            "dso_planetary_nebula",
            "dso_double_star",
            "dso_dark_nebula",
            "dso_supernova_remnant",
            "dso_nova_star",
            "dso_nonexistant",
            "dso_unknown",
            "dso_duplicate",
        ],
    ),
    (
        "Constellations",
        ["constellation_lines", "constellation_borders", "constellation_labels"],
    ),
    (
        "Sky Features",
        [
            "milky_way",
            "gridlines",
            "ecliptic",
            "celestial_equator",
            "galactic_equator",
            "horizon",
            "zenith",
            "optic_fov",
            "arrow",
            "tissot",
        ],
    ),
    (
        "Generic Shapes",
        ["line", "polygon", "circle", "ellipse", "rectangle", "marker", "text"],
    ),
]

# A few PlotStyle fields have no docstring in source -- short fallbacks for display.
DOC_FALLBACKS = {
    "tissot": "Default style for the Tissot indicatrix",
    "line": "Default style for lines plotted with `line()`",
    "polygon": "Default style for polygons plotted with `polygon()`",
    "circle": "Default style for circles plotted with `circle()`",
    "ellipse": "Default style for ellipses plotted with `ellipse()`",
    "rectangle": "Default style for rectangles plotted with `rectangle()`",
    "marker": "Default style for markers plotted with `marker()`",
}


# ---------------------------------------------------------------- extraction


def _unparse(node):
    return None if node is None else ast.unparse(node)


def _first_paragraph(doc):
    if not doc:
        return ""
    return " ".join(doc.strip().split("\n\n")[0].split())


def extract_classes(path: Path) -> dict:
    """Parses a styles module and returns {class_name: {bases, doc, fields}}."""
    tree = ast.parse(path.read_text())
    classes = {}

    for node in tree.body:
        if not isinstance(node, ast.ClassDef):
            continue

        fields = []
        body = node.body
        i = 0
        while i < len(body):
            stmt = body[i]
            if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
                doc = ""
                if i + 1 < len(body):
                    nxt = body[i + 1]
                    if (
                        isinstance(nxt, ast.Expr)
                        and isinstance(nxt.value, ast.Constant)
                        and isinstance(nxt.value.value, str)
                    ):
                        doc = nxt.value.value
                        i += 1
                fields.append(
                    {
                        "name": stmt.target.id,
                        "type": _unparse(stmt.annotation),
                        "default": _unparse(stmt.value),
                        "doc": _first_paragraph(doc),
                    }
                )
            i += 1

        classes[node.name] = {
            "bases": [_unparse(b) for b in node.bases],
            "doc": _first_paragraph(ast.get_docstring(node) or ""),
            "fields": fields,
        }

    return classes


# ---------------------------------------------------------- field resolution

_RESOLVED_FIELDS_CACHE: dict = {}
_LEAF_COUNT_CACHE: dict = {}


def resolve_fields(type_name: str, classes: dict) -> list:
    """Own fields plus everything inherited from base style classes (in MRO
    order), so e.g. ArrowStyle shows PolygonStyle's fields too, not just its
    own five."""
    if type_name in _RESOLVED_FIELDS_CACHE:
        return _RESOLVED_FIELDS_CACHE[type_name]

    cdef = classes[type_name]
    fields = []
    for base in cdef["bases"]:
        if base in classes:
            fields.extend(resolve_fields(base, classes))

    own_names = {f["name"] for f in cdef["fields"]}
    fields = [f for f in fields if f["name"] not in own_names]
    fields.extend(cdef["fields"])

    _RESOLVED_FIELDS_CACHE[type_name] = fields
    return fields


def core_type(ftype: str) -> str:
    return ftype.replace(" | None", "").strip()


def leaf_count(type_name: str, classes: dict) -> int:
    """Total number of plain (non-nested) properties reachable from a style
    type, counting through every nested style field."""
    if type_name in _LEAF_COUNT_CACHE:
        return _LEAF_COUNT_CACHE[type_name]

    total = 0
    for f in resolve_fields(type_name, classes):
        nested = core_type(f["type"])
        total += leaf_count(nested, classes) if nested in classes else 1

    _LEAF_COUNT_CACHE[type_name] = total
    return total


# --------------------------------------------------------------- doc markup

BRACKET_LINK = re.compile(r"\[([^\]]+)\]\[[^\]]+\]")
MD_LINK = re.compile(r"\[([^\]]+)\]\([^)]+\)")
BOLD = re.compile(r"\*\*([^*]+)\*\*")
EMPHASIS = re.compile(r"[*_]([^*_]+)[*_]")
SEE_PAREN = re.compile(r"\s*\(see [^)]*\)\.?\s*$", re.IGNORECASE)
BACKTICK = re.compile(r"`([^`]+)`")
FIELD_DEFAULT = re.compile(r"default=([^,)]+)")
COLOR_WRAP = re.compile(r"^Color\('(.+)'\)$")
ENUM_VALUE = re.compile(r"^[A-Za-z]+Enum\.([A-Za-z0-9_]+)$")


def clean_doc(doc: str) -> str:
    if not doc:
        return ""
    doc = BRACKET_LINK.sub(r"\1", doc)
    doc = MD_LINK.sub(r"\1", doc)
    doc = BOLD.sub(r"\1", doc)
    doc = EMPHASIS.sub(r"\1", doc)
    doc = SEE_PAREN.sub("", doc)
    return doc.strip()


def render_doc(doc: str, limit: int = 1024) -> tuple[str, str]:
    """Returns (short markup-safe html with `code` spans for backticks, full
    plain text if it was truncated else "")."""
    doc = clean_doc(doc)
    if not doc:
        return "", ""

    short = doc
    truncated = False
    if len(doc) > limit:
        short = doc[:limit].rsplit(" ", 1)[0]
        truncated = True

    rendered = BACKTICK.sub(r"<code>\1</code>", htmlmod.escape(short, quote=True))
    if truncated:
        # a numeric character reference instead of a literal "…" -- this
        # HTML gets served from several different places (a plain dev
        # server while testing, mkdocs/zensical once embedded), and not
        # all of them declare a charset, so a raw non-ASCII byte here is
        # at the mercy of whatever encoding the browser guesses.
        rendered += "&#8230;"
    return rendered, (doc if truncated else "")


def render_default(default: str | None):
    """Returns (display value, is_color) for a leaf field's default, or
    None if there's nothing worth showing."""
    if default is None:
        return None

    m = COLOR_WRAP.match(default)
    if m:
        return m.group(1), True

    m = ENUM_VALUE.match(default)
    if m:
        return m.group(1), False

    if default.startswith("Field("):
        m = FIELD_DEFAULT.search(default)
        return (m.group(1), False) if m else (default, False)

    if default == "None":
        return "none", False

    if default.startswith("'") and default.endswith("'"):
        return default[1:-1], False

    return default, False


# ---------------------------------------------------------------- tree data


def build_leaf(field: dict, path: str) -> dict:
    doc_html, doc_full = render_doc(field["doc"])
    default = render_default(field["default"])

    return {
        "kind": "leaf",
        "name": field["name"],
        "type": field["type"],
        "default_value": default[0] if default else None,
        "is_color": default[1] if default else False,
        "doc_html": doc_html,
        "doc_full": doc_full,
        "search_doc": field["doc"].lower(),
        "path": path,
    }


def build_node(name: str, type_name: str, doc: str, classes: dict, path: str) -> dict:
    """Builds one property as a tree node: its own identity, plus every
    field of its style type (each itself a node or a leaf), so the whole
    subtree is available to render in place -- no separate lookup elsewhere."""
    cdef = classes[type_name]
    doc_html, doc_full = render_doc(doc or cdef["doc"])

    children = []
    for f in resolve_fields(type_name, classes):
        nested = core_type(f["type"])
        child_path = f"{path}.{f['name']}"
        if nested in classes:
            children.append(
                build_node(f["name"], nested, f["doc"], classes, child_path)
            )
        else:
            children.append(build_leaf(f, child_path))

    # Every nested style type here is a BaseStyle subclass (that's what
    # makes it a node instead of a leaf) -- push those last so a style's
    # plain values (padding, opacity, ...) read before its nested styles
    # (background, marker, ...), a stable sort so declaration order still
    # holds within each group.
    children.sort(key=lambda c: c["kind"] == "node")

    return {
        "kind": "node",
        "name": name,
        "type_name": type_name,
        "doc_html": doc_html,
        "doc_full": doc_full,
        "children": children,
    }


def build_groups(plot_fields: dict, classes: dict) -> list:
    groups = []
    for group_name, field_names in GROUPS:
        nodes = []
        for fname in field_names:
            f = plot_fields[fname]
            doc = f["doc"] or DOC_FALLBACKS.get(fname, "")
            path = f"style.{fname}"
            nodes.append(build_node(fname, core_type(f["type"]), doc, classes, path))
        groups.append({"name": group_name, "nodes": nodes})
    return groups


# ------------------------------------------------------------------- page


def build_html(plot_fields: dict, classes: dict) -> str:
    groups = build_groups(plot_fields, classes)
    total_leaves = sum(
        leaf_count(core_type(plot_fields[name]["type"]), classes)
        for _, names in GROUPS
        for name in names
    )
    total_elements = sum(len(names) for _, names in GROUPS)

    env = Environment(
        loader=FileSystemLoader(SCRIPT_DIR),
        autoescape=select_autoescape(["html", "jinja"]),
    )
    template = env.get_template("style_reference.html")
    return template.render(
        groups=groups,
        total_elements=total_elements,
        total_leaves=total_leaves,
    )


def main():
    elements_classes = extract_classes(STYLES_DIR / "elements.py")
    plot_classes = extract_classes(STYLES_DIR / "plot.py")
    plot_fields = {f["name"]: f for f in plot_classes["PlotStyle"]["fields"]}

    html = build_html(plot_fields, elements_classes)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(html)
    print(f"Wrote {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
