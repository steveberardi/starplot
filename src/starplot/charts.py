from datetime import datetime

from adjustText import adjust_text

from matplotlib import pyplot as plt, patheffects as pe
from matplotlib.collections import LineCollection

from skyfield.api import Star, load, wgs84
from skyfield.positionlib import position_of_radec
from skyfield.projections import build_stereographic_projection

from pytz import timezone

from starplot.constellations import (
    create_projected_constellation_lines,
    labels as conlabels,
)
from starplot.dsos import messier
from starplot.stars import get_star_data, star_names
from starplot.styles import PlotStyle, MONO
from starplot.utils import in_circle

DSO_BASE = [
    "M5",
    "M13",
    "M23",
    "M42",
    "M44",
    "M45",
]


def get_position(lat: float, lon: float, dt: datetime, tz: str = "UTC"):
    ts = load.timescale()
    t = ts.from_datetime(timezone(tz).localize(dt))
    loc = wgs84.latlon(lat, lon).at(t)
    return t, loc.from_altaz(alt_degrees=90, az_degrees=0)


def create_star_chart(
    lat: float,
    lon: float,
    dt: datetime,
    filename: str,
    tz_identifier: str = "UTC",
    style: PlotStyle = MONO,
    limiting_magnitude: float = 4.6,
    limiting_magnitude_labels: float = 2,
    figure_size: int = 16,
    figure_dpi: int = 200,
    *args,
    **kwargs
):
    t, position = get_position(
        lat=lat,
        lon=lon,
        dt=dt,
        tz=tz_identifier,
    )

    eph = load("de421.bsp")
    earth = eph["earth"]

    project_fn = build_stereographic_projection(position)
    stardata = get_star_data()
    labels = []

    # project stars to stereographic plot
    star_positions = earth.at(t).observe(Star.from_dataframe(stardata))
    stardata["x"], stardata["y"] = project_fn(star_positions)

    # filter stars by limiting magnitude
    bright_stars = stardata.magnitude <= limiting_magnitude

    # calculate size of each star based on magnitude
    sizes = []
    for m in stardata["magnitude"][bright_stars]:
        if m < 2:
            sizes.append((6 - m) ** 2.26)
        else:
            sizes.append((1 + limiting_magnitude - m) ** 2)

    # create plot
    fig, ax = plt.subplots(figsize=[figure_size, figure_size])

    # Draw constellation lines
    constellations = LineCollection(
        create_projected_constellation_lines(stardata),
        colors=style.constellation_line_color.as_hex(),
        linewidths=style.constellation_line_width,
        zorder=-1,
        alpha=style.constellation_line_alpha,
    )
    cons = ax.add_collection(constellations)

    # Draw stars
    starx = ax.scatter(
        stardata["x"][bright_stars],
        stardata["y"][bright_stars],
        sizes,
        color=style.star_color.as_hex(),
    )

    starpos_x = []
    starpos_y = []

    # Plot star names
    for i, s in stardata[bright_stars].iterrows():
        if (
            in_circle(s["x"], s["y"])
            and i in star_names
            and s["magnitude"] < limiting_magnitude_labels
        ):
            label = ax.text(
                s["x"] + 0.00984,
                s["y"] - 0.006,
                star_names[i],
                color=style.star_font_color.as_hex(),
                ha="left",
                va="top",
                fontsize=style.star_font_size,
                weight=style.star_font_weight,
                zorder=1,
                path_effects=[
                    pe.withStroke(
                        linewidth=2, foreground=style.background_color.as_hex()
                    )
                ],
            )
            label.set_alpha(style.star_font_alpha)
            labels.append(label)
            starpos_x.append(s["x"])
            starpos_y.append(s["y"])

    # Plot constellation names
    for con in conlabels:
        fullname, ra, dec = conlabels.get(con)
        x, y = project_fn(position_of_radec(ra, dec))

        if in_circle(x, y) and fullname:
            label = ax.text(
                x,
                y,
                fullname.upper(),
                color=style.constellation_font_color.as_hex(),
                fontsize=style.constellation_font_size,
                weight=style.constellation_font_weight,
                zorder=1,
                path_effects=[
                    pe.withStroke(
                        linewidth=2, foreground=style.background_color.as_hex()
                    )
                ],
            )
            label.set_alpha(0.6)
            labels.append(label)

    # Plot DSO objects
    for m in DSO_BASE:
        ra, dec = messier.get(m)
        x, y = project_fn(position_of_radec(ra, dec))

        if in_circle(x, y):
            ax.plot(
                x,
                y,
                marker="^",
                markersize=4,
                color=style.star_color.as_hex(),
                fillstyle="none",
                linestyle="--"
            )
            label = ax.text(
                x + 0.005,
                y + 0.005,
                m.upper(),
                ha="right",
                va="center",
                color=style.constellation_font_color.as_hex(),
                fontsize=style.constellation_font_size,
                weight=style.constellation_font_weight,
                zorder=1,
                path_effects=[
                    pe.withStroke(
                        linewidth=2, foreground=style.background_color.as_hex()
                    )
                ],
            )
            labels.append(label)

    ax.set_xlim(-1.1, 1.1)
    ax.set_ylim(-1.1, 1.1)
    ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(False)
    ax.set_aspect(1.0)
    plt.axis("off")

    # Plot border text
    border_font_kwargs = dict(
        fontsize=style.border_font_size,
        weight=style.border_font_weight,
        color=style.border_font_color.as_hex(),
    )
    ax.text(0, 1.009, "N", **border_font_kwargs)
    ax.text(1.003, 0, "W", **border_font_kwargs)
    ax.text(-1.042, 0, "E", **border_font_kwargs)
    ax.text(0, -1.045, "S", **border_font_kwargs)

    # Inner border circle
    circle = plt.Circle(
        (0, 0),
        facecolor=style.background_color.as_hex(),
        radius=1.0,
        linewidth=2,
        edgecolor=style.border_line_color.as_hex(),
        fill=True,
        zorder=-100,
    )
    ax.add_patch(circle)

    # clip stars outside border circle
    starx.set_clip_path(circle)
    cons.set_clip_path(circle)

    # Outer border circle
    circle2 = plt.Circle(
        (0, 0),
        facecolor=style.border_bg_color.as_hex(),
        radius=1.06,
        linewidth=4,
        edgecolor=style.border_line_color.as_hex(),
        fill=True,
        zorder=-200,
    )
    ax.add_patch(circle2)

    # adjust text to avoid collisions
    adjust_text(labels, starpos_x, starpos_y)

    fig.savefig(
        filename, bbox_inches="tight", pad_inches=0, edgecolor=None, dpi=figure_dpi
    )
