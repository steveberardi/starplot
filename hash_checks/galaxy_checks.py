from pathlib import Path

from starplot import GalaxyPlot, _, styles

HERE = Path(__file__).resolve().parent
DATA_PATH = HERE / "data"

STYLE = styles.PlotStyle().extend(
    styles.extensions.BLUE_NIGHT,
    styles.extensions.MAP,
    {"figure": {"background": {"fill": None}}},
)

RESOLUTION = 2000


def _galaxy():
    p = GalaxyPlot(style=STYLE)
    p.gridlines()
    p.galactic_equator(num_labels=2)
    p.milky_way()
    p.stars(
        where=[_.magnitude < 7],
        where_labels=[False],
    )
    p.open_clusters(
        where=[_.magnitude < 9],
        where_labels=False,
        where_true_size=False,
    )
    return p


def check_galaxy_base():
    filename = DATA_PATH / "galaxy-base.png"
    galaxy_base = _galaxy()
    galaxy_base.export(filename)
    return filename
