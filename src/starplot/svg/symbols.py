from starplot.styles import MarkerSymbolEnum

"""
(0,0)          (100,0)
  ┌──────────────┐
  │              │
  │   (50,50)    │
  │              │
  └──────────────┘
(0,100)        (100,100)
"""



def circle_cross(x, y, size, css):
    r = round(size / 2, 4)
    return (
        f"\t<g {css}>\n"
        f'\t\t<circle cx="{x}" cy="{y}" r="{r}" />\n'
        f'\t\t<line x1="{x - r}" y1="{y}" x2="{x + r}" y2="{y}"/>\n'
        f'\t\t<line x1="{x}" y1="{y + r}" x2="{x}"  y2="{y - r}"/>\n'
        "\t</g>\n"
    )


def circle_crosshair(x, y, size, css):
    r = size / 2
    n = round(1.75 * r, 4)
    return (
        f"\t<g {css}>\n"
        f'\t\t<circle cx="{x}" cy="{y}" r="{r}" />\n'
        f'\t\t<line x1="{x}" y1="{y-r}" x2="{x}" y2="{y - n}"/>\n'
        f'\t\t<line x1="{x + r}" y1="{y}" x2="{x + n}" y2="{y}"/>\n'
        f'\t\t<line x1="{x}" y1="{y + r}" x2="{x}" y2="{y + n}"/>\n'
        f'\t\t<line x1="{x - r}" y1="{y}" x2="{x - n}"  y2="{y}"/>\n'
        "\t</g>\n"
    )


def circle(x, y, size, css):
    return f'\t<circle cx="{x}" cy="{y}" r="{size/2}" {css} />\n'


def ellipse(x, y, size, css):
    rx = round(size * 0.5, 4)
    ry = round(size * 0.3, 4)
    return f'\t<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" transform="rotate(-20, {x}, {y})" {css} />\n'


def use(id, cx, cy, height, width, attrs, css_class=""):
    x = cx - width / 2
    y = cy - height / 2

    return f'<use href="#{id}" x="{x}" y="{y}" width="{width}" height="{height}" {attrs} class="{css_class}"/>'


SYMBOL_FUNCTIONS = {
    MarkerSymbolEnum.POINT: circle,
    MarkerSymbolEnum.CIRCLE: circle,
    MarkerSymbolEnum.CIRCLE_CROSS: circle_cross,
    MarkerSymbolEnum.CIRCLE_CROSSHAIR: circle_crosshair,
    MarkerSymbolEnum.ELLIPSE: ellipse,
}


def create(x, y, size, symbol: MarkerSymbolEnum, css: str = ""):
    return SYMBOL_FUNCTIONS.get(symbol)(x, y, size, css)
