"""
Generates an HTML page that previews every font Starplot can find on this
system (via starplot.svg.fonts.build_font_index), grouped by family, with
each weight/style variant shown in its own actual typeface.

The page references font files directly from disk with file:// URLs (rather
than embedding them), since build_font_index() scans the whole system and
can turn up hundreds of fonts -- embedding all of them would make for a
huge, slow-to-generate file. That also means the output is only useful on
the machine it was generated on.
"""

from collections import defaultdict
from pathlib import Path

from starplot.svg.fonts import build_font_index

OUTPUT_PATH = Path(__file__).resolve().parent / "temp" / "fonts.html"

WEIGHT_NAMES = {
    100: "Thin",
    200: "Extra Light",
    300: "Light",
    400: "Regular",
    500: "Medium",
    600: "SemiBold",
    700: "Bold",
    800: "Extra Bold",
    900: "Black",
}

PREVIEW_TEXT = "The quick brown fox jumps over the lazy dog"

STYLE = """
    body {
        margin: 0;
        padding: 40px;
        background: #f4f5f7;
        color: #1a1a1a;
        font-family: -apple-system, Helvetica, Arial, sans-serif;
    }
    h1 {
        font-size: 1.4em;
        margin-bottom: 4px;
    }
    .subtitle {
        color: #666;
        margin-bottom: 20px;
    }
    #font-search {
        display: block;
        width: 100%;
        max-width: 420px;
        box-sizing: border-box;
        font-size: 1em;
        padding: 10px 14px;
        margin-bottom: 28px;
        border: 1px solid #ccc;
        border-radius: 8px;
        outline: none;
    }
    #font-search:focus {
        border-color: #888;
    }
    .family {
        background: #fff;
        border: 1px solid #ddd;
        border-radius: 10px;
        padding: 20px 24px;
        margin-bottom: 20px;
    }
    .family h2 {
        font-size: 1.1em;
        margin: 0 0 14px 0;
        display: flex;
        align-items: baseline;
        gap: 8px;
    }
    .family h2 .count {
        font-size: 0.7em;
        font-weight: normal;
        color: #888;
    }
    .variant {
        padding: 10px 0;
        border-top: 1px solid #eee;
    }
    .variant:first-of-type {
        border-top: none;
    }
    .variant-label {
        font-size: 0.72em;
        color: #888;
        font-family: ui-monospace, Menlo, monospace;
        margin-bottom: 2px;
    }
    .variant-preview {
        font-size: 1.5em;
        overflow-wrap: anywhere;
    }
"""


def slugify(family: str) -> str:
    return "".join(c if c.isalnum() else "-" for c in family).strip("-")


def variant_label(weight: int, italic: bool) -> str:
    name = WEIGHT_NAMES.get(weight, str(weight))
    label = f"{name} ({weight})"
    if italic:
        label += " Italic"
    return label


def build_html() -> str:
    font_index = build_font_index()

    families = defaultdict(list)
    for (family, weight, italic), path in font_index.items():
        families[family].append((weight, italic, path))

    font_faces = []
    family_sections = []

    for family in sorted(families):
        variants = sorted(families[family], key=lambda v: (v[0], v[1]))
        slug = slugify(family)

        variant_rows = []
        for weight, italic, path in variants:
            font_url = Path(path).resolve().as_uri()
            font_format = "opentype" if path.suffix.lower() == ".otf" else "truetype"
            style = "italic" if italic else "normal"

            font_faces.append(
                f"""@font-face {{
    font-family: "{slug}";
    src: url("{font_url}") format("{font_format}");
    font-weight: {weight};
    font-style: {style};
}}"""
            )

            variant_rows.append(f"""
            <div class="variant">
                <div class="variant-label">{variant_label(weight, italic)} &middot; {path.name}</div>
                <div class="variant-preview" style="font-family:'{slug}'; font-weight:{weight}; font-style:{style};">{PREVIEW_TEXT}</div>
            </div>""")

        plural = "s" if len(variants) != 1 else ""
        variant_rows_html = "".join(variant_rows)
        family_sections.append(f"""
        <section class="family" data-family="{family}">
            <h2>{family.title()} <span class="count">{len(variants)} variant{plural}</span></h2>
            {variant_rows_html}
        </section>""")

    font_faces_css = "\n".join(font_faces)
    family_sections_html = "".join(family_sections)

    return f"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>Starplot Fonts</title>
<style>
{STYLE}
{font_faces_css}
</style>
</head>
<body>
<h1>Fonts found by Starplot</h1>
<div class="subtitle">{len(font_index)} variants across {len(families)} families</div>
<input type="text" id="font-search" placeholder="Search fonts&hellip;" autocomplete="off">
{family_sections_html}
<script>
    var searchInput = document.getElementById("font-search");
    var families = document.querySelectorAll(".family");

    searchInput.addEventListener("input", function () {{
        var query = searchInput.value.trim().toLowerCase();
        families.forEach(function (section) {{
            var match = section.getAttribute("data-family").indexOf(query) !== -1;
            section.style.display = match ? "" : "none";
        }});
    }});
</script>
</body>
</html>
"""


def main():
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(build_html())
    print(f"Wrote {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
