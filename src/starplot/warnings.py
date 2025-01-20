import warnings

import matplotlib


def suppress():
    # ignore noisy matplotlib warnings
    warnings.filterwarnings(
        "ignore",
        message="Setting the 'color' property will override the edgecolor or facecolor properties",
    )

    # Silence various matplotlib logs (e.g. building font cache)
    matplotlib.set_loglevel("critical")

    # Silence all user warnings
    warnings.filterwarnings("ignore", category=UserWarning)

    # Silence noisy cartopy warnings
    warnings.filterwarnings("ignore", module="cartopy")
    warnings.filterwarnings("ignore", module="shapely")
