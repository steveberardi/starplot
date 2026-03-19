from starplot.styles import MarkerStyle, MarkerSymbolEnum

"""
(0,0)          (100,0)
  ┌──────────────┐
  │              │
  │   (50,50)    │
  │              │
  └──────────────┘
(0,100)        (100,100)
"""


def get(style: MarkerStyle):
    return {
        MarkerSymbolEnum.CIRCLE: circle,
        MarkerSymbolEnum.CIRCLE_CROSS: circle_cross,
        MarkerSymbolEnum.CIRCLE_CROSSHAIR: circle_crosshair,
        MarkerSymbolEnum.POINT: circle,
    }.get(style.symbol)()


def circle_cross():
    symbol_id = "symbol-circle-cross"

    return symbol_id, (
        f'<symbol id="{symbol_id}" viewBox="-1 -1 2 2" overflow="visible">'
        '\t<circle cx="0" cy="0" r="1" />'
        '\t<line x1="-1" y1="0" x2="1" y2="0"/>'
        '\t<line x1="0" y1="-1" x2="0" y2="1"/>'
        "</symbol>"
    )


def circle_crosshair():
    symbol_id = "symbol-circle-crosshair"

    return symbol_id, (
        f'<symbol id="{symbol_id}" viewBox="0 0 100 100" overflow="visible">'
        '<circle cx="50" cy="50" r="25" />'
        '<line x1="50" y1="25" x2="50" y2="0"/>'
        '<line x1="75" y1="50" x2="100" y2="50"/>'
        '<line x1="50" y1="75" x2="50" y2="100"/>'
        '<line x1="25" y1="50" x2="0"  y2="50"/>'
        "</symbol>"
    )


def circle():
    symbol_id = "symbol-circle"
    return symbol_id, (
        f'\t<symbol id="{symbol_id}" viewBox="0 0 100 100" overflow="visible">\n'
        '\t\t<circle cx="50" cy="50" r="50" />\n'
        "\t</symbol>\n"
    )


def use(id, cx, cy, height, width, attrs, css_class=""):
    x = cx - width / 2
    y = cy - height / 2

    return f'<use href="#{id}" x="{x}" y="{y}" width="{width}" height="{height}" {attrs} class="{css_class}"/>'
