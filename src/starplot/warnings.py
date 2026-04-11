import warnings

def suppress():
    # Silence all user warnings
    warnings.filterwarnings("ignore", category=UserWarning)

    # Silence noisy shapely warnings
    warnings.filterwarnings("ignore", module="shapely")
