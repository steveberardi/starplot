from starplot.styles.base import (
    FontWeightEnum,
    FillStyleEnum,
    LineStyleEnum,
)


MAP = dict(
    star={"label": {"font_size": 8}},
    bayer_labels={"font_size": 7},
    constellation={
        "line": {"width": 3},
        "label": {"font_size": 11, "font_weight": FontWeightEnum.LIGHT},
    },
    ecliptic={"line": {"width": 2, "alpha": 0.8}},
)

ZENITH = dict(
    ecliptic={
        "line": {"visible": False},
        "label": {"visible": False},
    },
)


# ---------------------------------------------------
# Color Schemes

GRAYSCALE = dict(
    background_color="#fff",
    # Borders
    border_font_color="#000",
    border_line_color="#000",
    border_bg_color="#fff",
    # Constellations
    constellation={
        "line": {
            "color": "#c8c8c8",
        },
    },
    # Milky Way
    milky_way={
        "color": "#d9d9d9",
        "alpha": 0.36,
        "edge_width": 0,
    },
    planets={
        "marker": {
            "color": "#000",
            "fill": FillStyleEnum.LEFT,
        },
    },
    ecliptic={
        "line": {"color": "#777"},
        "label": {"color": "#777"},
    },
    celestial_equator={
        "line": {"color": "#999"},
        "label": {"color": "#999"},
    },
    dso_open_cluster={
        "marker": {
            "color": "#000",
        },
    },
    dso_galaxy={
        "marker": {"color": "#000"},
    },
    dso_nebula={
        "marker": {"color": "#000"},
    },
    dso_double_star={
        "marker": {"color": "#000"},
    },
)

BLUE_LIGHT = dict(
    background_color="#fff",
    # Borders
    border_font_color="#f1f6ff",
    border_line_color="#2f4358",
    border_bg_color="#fff",
    # Constellations
    constellation={
        "line": {
            "width": 3,
            "color": "#6ba832",
            "alpha": 0.3,
        },
        "label": {
            "font_color": "#c5c5c5",
        },
    },
    # Milky Way
    milky_way={
        "color": "#94c5e3",
        "alpha": 0.16,
        "edge_width": 0,
    },
    planets={
        "marker": {
            "color": "#f89d00",
            "alpha": 0.4,
            "fill": FillStyleEnum.FULL,
        },
    },
    ecliptic={
        "line": {"color": "#e33b3b"},
        "label": {"color": "#e33b3b"},
    },
    celestial_equator={
        "line": {"color": "#2d5ec2"},
        "label": {"color": "#2d5ec2"},
    },
    dso_open_cluster={
        "marker": {
            "color": "#fffb68",
            "alpha": 0.3,
        },
        "label": {"visible": False},
    },
    dso_galaxy={
        "marker": {"color": "hsl(18, 68%, 75%)", "alpha": 0.5},
    },
    dso_nebula={
        "marker": {"color": "hsl(91, 53%, 75%)", "alpha": 0.5},
    },
    dso_double_star={
        "marker": {"alpha": 0.6},
    },
)

BLUE_MEDIUM = dict(
    background_color="#f1f6ff",
    # Borders
    border_font_color="#f1f6ff",
    border_line_color="#2f4358",
    border_bg_color="#7997b9",
    # Constellations
    constellation=dict(
        line=dict(width=3, color="#6ba832", alpha=0.2),
        label=dict(font_size=7, font_weight=FontWeightEnum.LIGHT),
    ),
    planets={
        "marker": {"color": "#f89d00", "alpha": 0.4, "fill": FillStyleEnum.FULL},
    },
    ecliptic={
        "line": {"color": "#e33b3b"},
        "label": {"color": "#e33b3b"},
    },
    celestial_equator={
        "line": {"color": "#2d5ec2"},
        "label": {"color": "#2d5ec2"},
    },
)

BLUE_DARK = dict(
    background_color="#4c566a",
    # Borders
    border_font_color="#a3be8c",
    border_line_color="#a3be8c",
    border_bg_color="#2e3440",
    # Stars
    star=dict(
        marker=dict(color="#88c0d0"),
        label=dict(font_size=9, font_color="#88c0d0", font_weight=FontWeightEnum.BOLD),
    ),
    bayer_labels={"font_color": "#85c9de", "font_alpha": 0.8},
    milky_way=dict(
        color="#95a3bf",
        alpha=0.14,
        edge_width=0,
        zorder=-10000,
    ),
    gridlines=dict(
        line=dict(
            color="#888",
            width=1,
            style=LineStyleEnum.SOLID,
            alpha=0.8,
            zorder=-10_000,
        ),
        label=dict(
            font_size=12,
            font_color="#c2d2f3",
            font_weight=FontWeightEnum.LIGHT,
            font_alpha=0.8,
        ),
    ),
    # DSOs
    dso=dict(
        marker=dict(
            color="rgb(230, 204, 147)",
            size=4,
            fill=FillStyleEnum.FULL,
            alpha=0.46,
        ),
        label=dict(
            font_size=7,
            font_color="rgb(230, 204, 147)",
            font_weight=FontWeightEnum.LIGHT,
            font_alpha=0.6,
        ),
    ),
    # Constellations
    constellation=dict(
        line=dict(width=2, color="rgb(230, 204, 147)", alpha=0.36),
        label=dict(
            font_size=7,
            font_weight=FontWeightEnum.LIGHT,
            font_color="rgb(230, 204, 147)",
            font_alpha=0.6,
        ),
    ),
    planets={
        "marker": {"color": "#A69777", "alpha": 0.6, "fill": FillStyleEnum.FULL},
    },
    ecliptic={"line": {"color": "#D99CBA"}, "label": {"color": "#D99CBA"}},
    celestial_equator={"line": {"color": "#77A67F"}, "label": {"color": "#77A67F"}},
    dso_open_cluster={
        "marker": {"color": "#d8d99c", "alpha": 0.45},
        "label": {"visible": False},
    },
    dso_galaxy={
        "marker": {"color": "#D99CBA", "alpha": 0.45},
    },
    dso_nebula={
        "marker": {"color": "#9CD9BB", "alpha": 0.45},
    },
    dso_double_star={
        "marker": {"alpha": 0.6},
    },
)

# Helpers

HIDE_LABELS = dict(
    star={"label": {"visible": False}},
    constellation={"label": {"visible": False}},
    planets={"label": {"visible": False}},
    ecliptic={"label": {"visible": False}},
    celestial_equator={"label": {"visible": False}},
    dso={"label": {"visible": False}},
    gridlines={"label": {"visible": False}},
    bayer_labels={"visible": False},

)