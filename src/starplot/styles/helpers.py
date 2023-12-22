from starplot.styles import PlotStyle, extensions

BASE = PlotStyle()

# Optic Plots
OPTIC_BASE = BASE.extend(extensions.OPTIC)

# Map Plots
MAP_BASE = BASE.extend(extensions.MAP)
MAP_BLUE_LIGHT = MAP_BASE.extend(extensions.BLUE_LIGHT)
MAP_BLUE_MEDIUM = MAP_BASE.extend(extensions.BLUE_MEDIUM)
MAP_BLUE_DARK = MAP_BASE.extend(extensions.BLUE_DARK)
MAP_GRAYSCALE = MAP_BASE.extend(extensions.GRAYSCALE)

# Zenith Plots
ZENITH_BASE = BASE.extend(extensions.ZENITH)
ZENITH_BLUE_LIGHT = ZENITH_BASE.extend(extensions.BLUE_LIGHT)
ZENITH_BLUE_MEDIUM = ZENITH_BASE.extend(extensions.BLUE_MEDIUM)
ZENITH_BLUE_DARK = ZENITH_BASE.extend(extensions.BLUE_DARK)
ZENITH_GRAYSCALE = ZENITH_BASE.extend(extensions.GRAYSCALE)


BLUE_LIGHT = BASE.extend(extensions.BLUE_LIGHT)
BLUE_MEDIUM = BASE.extend(extensions.BLUE_MEDIUM)
BLUE_DARK = BASE.extend(extensions.BLUE_DARK)
GRAYSCALE = BASE.extend(extensions.GRAYSCALE)
