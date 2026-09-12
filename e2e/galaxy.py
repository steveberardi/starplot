from utils import actual_filename

from starplot import GalaxyPlot, _, styles

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
        where=[_.magnitude < 6],
        where_labels=False,
    )
    p.open_clusters(
        where=[_.magnitude < 9],
        where_labels=False,
        where_true_size=False,
    )
    return p


def e2e_galaxy_base():
    filename = actual_filename("galaxy_base")
    galaxy_base = _galaxy()
    galaxy_base.export(filename)
    return filename
