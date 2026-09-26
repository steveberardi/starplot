"""
Generates an HTML reference page for every style property on PlotStyle,
as a collapsible tree.

Since many properties share the same underlying style type (most DSOs, planets,
the moon, and the sun are all ObjectStyle, for example), that type's fields
get repeated at every place it's used -- deliberately, so each branch of
the tree is self-contained and expands right where it is instead of
jumping elsewhere on the page.

This module only extracts and shapes the data; the page's HTML, CSS, and
JS all live in the Jinja2 template style_explorer.html, next to this file.

This code was created via Claude Code.
"""

import ast
import html as htmlmod
import re
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
STYLES_DIR = REPO_ROOT / "src" / "starplot" / "styles"
SCRIPT_DIR = Path(__file__).resolve().parent
OUTPUT_PATH = REPO_ROOT / "docs" / "images" / "reference" / "style_explorer.html"

# Groups of PlotStyle's own properties, in the order they should appear.
GROUPS = [
    ("Layout", ["base", "axes", "figure", "title", "table", "legend"]),
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
                        "default_node": stmt.value,
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


def call_kwargs(node) -> dict:
    """If `node` is a class-instantiation call (e.g. the `MarkerStyle(...)`
    a PlotStyle field like `dso_open_cluster` sets for its `marker` field),
    returns {kwarg_name: value_ast_node} for its keyword arguments -- the
    field values that *instance* overrides, as opposed to the underlying
    style class's own field defaults. `{}` for anything else (no override,
    or an override that isn't itself a call, e.g. `label=None`)."""
    if not isinstance(node, ast.Call):
        return {}
    return {kw.arg: kw.value for kw in node.keywords if kw.arg is not None}


def split_top_level(s: str, sep: str) -> list[str]:
    """Splits `s` on `sep`, but only where it's not nested inside brackets
    (e.g. won't split the commas inside `Literal["a", "b"]` when splitting
    a union type on `|`)."""
    parts = []
    depth = 0
    current = ""
    for ch in s:
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth -= 1
        if ch == sep and depth == 0:
            parts.append(current.strip())
            current = ""
        else:
            current += ch
    parts.append(current.strip())
    return parts


LITERAL_TYPE = re.compile(r"^Literal\[(.*)\]$")


def literal_type_lines(ftype: str) -> list[str] | None:
    """If a field's type annotation contains a `Literal[...]` anywhere in
    its top-level union (e.g. `Literal["solid", "dashed"] | tuple[int] |
    None`), returns one line per union member, with the Literal's own
    values each expanded onto their own line too -- e.g. ['\\'solid\\'',
    '\\'dashed\\'', 'tuple[int]', 'None']. Returns None for a type with no
    Literal, so the caller can fall back to the plain single-line display."""
    members = split_top_level(ftype, "|")
    if not any(LITERAL_TYPE.match(m) for m in members):
        return None

    lines = []
    for member in members:
        m = LITERAL_TYPE.match(member)
        if m:
            lines.extend(split_top_level(m.group(1), ","))
        else:
            lines.append(member)
    return lines


# ---------------------------------------------------------- field resolution

_RESOLVED_FIELDS_CACHE: dict = {}


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


# --------------------------------------------------------------- doc markup

BRACKET_LINK = re.compile(r"\[([^\]]+)\]\[[^\]]+\]")
MD_LINK = re.compile(r"\[([^\]]+)\]\([^)]+\)")
BOLD = re.compile(r"\*\*([^*]+)\*\*")
EMPHASIS = re.compile(r"[*_]([^*_]+)[*_]")
SEE_PAREN = re.compile(r"\s*\(see [^)]*\)\.?\s*$", re.IGNORECASE)
BACKTICK = re.compile(r"`([^`]+)`")
FIELD_DEFAULT = re.compile(r"default=([^,)]+)")
COLOR_WRAP = re.compile(r"^Color\('(.+)'\)$")


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

    if default.startswith("Field("):
        m = FIELD_DEFAULT.search(default)
        return (m.group(1), False) if m else (default, False)

    if default == "None":
        return "None", False

    if default.startswith("'") and default.endswith("'"):
        return f'"{default[1:-1]}"', False

    return default, False


# ---------------------------------------------------------------- tree data


def build_leaf(field: dict, path: str, override_node=None) -> dict:
    doc_html, doc_full = render_doc(field["doc"])
    default_str = (
        _unparse(override_node) if override_node is not None else field["default"]
    )
    default = render_default(default_str)

    return {
        "kind": "leaf",
        "name": field["name"],
        "type": field["type"],
        "type_lines": literal_type_lines(field["type"]),
        "default_value": default[0] if default else None,
        "is_color": default[1] if default else False,
        "doc_html": doc_html,
        "doc_full": doc_full,
        "search_doc": field["doc"].lower(),
        "path": path,
    }


def build_node(
    name: str,
    type_name: str,
    doc: str,
    classes: dict,
    path: str,
    override_node=None,
) -> dict:
    """Builds one property as a tree node: its own identity, plus every
    field of its style type (each itself a node or a leaf), so the whole
    subtree is available to render in place -- no separate lookup elsewhere.

    `override_node` is the AST value of the specific PlotStyle instance
    this node came from (e.g. `dso_open_cluster`'s `MarkerStyle(...)` call
    for its `marker` field) -- its keyword arguments take precedence over
    the style class's own field defaults, since that's what a user actually
    gets when they use e.g. `dso_open_cluster`, not MarkerStyle's defaults."""
    cdef = classes[type_name]
    raw_doc = doc or cdef["doc"]
    doc_html, doc_full = render_doc(raw_doc)

    override_kwargs = call_kwargs(override_node)

    children = []
    for f in resolve_fields(type_name, classes):
        nested = core_type(f["type"])
        child_path = f"{path}.{f['name']}"
        child_override = override_kwargs.get(f["name"])
        if nested in classes:
            children.append(
                build_node(
                    f["name"],
                    nested,
                    f["doc"],
                    classes,
                    child_path,
                    child_override,
                )
            )
        else:
            children.append(build_leaf(f, child_path, child_override))

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
        "search_doc": raw_doc.lower(),
        "path": path,
        "children": children,
    }


def build_groups(plot_fields: dict, classes: dict) -> list:
    groups = []
    for group_name, field_names in GROUPS:
        nodes = []
        for fname in field_names:
            f = plot_fields[fname]
            doc = f["doc"] or ""
            path = f"style.{fname}"
            nodes.append(
                build_node(
                    fname,
                    core_type(f["type"]),
                    doc,
                    classes,
                    path,
                    f["default_node"],
                )
            )
        groups.append({"name": group_name, "nodes": nodes})
    return groups


# ------------------------------------------------------------------- page


def build_html(plot_fields: dict, classes: dict) -> str:
    groups = build_groups(plot_fields, classes)

    env = Environment(
        loader=FileSystemLoader(SCRIPT_DIR),
        autoescape=select_autoescape(["html", "jinja"]),
    )
    template = env.get_template("style_explorer.html")
    return template.render(groups=groups)


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
