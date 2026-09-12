import inspect
from pathlib import Path

ACTUAL_PATH = Path(__file__).resolve().parent / "actual"


def actual_filename(name: str) -> Path:
    """
    Returns a Path for an actual SVG file, under a subdirectory named after
    the calling .py file (e.g. a call from map.py goes in actual/map/).
    """
    caller_module = Path(inspect.stack()[1].filename).stem
    directory = ACTUAL_PATH / caller_module
    directory.mkdir(parents=True, exist_ok=True)
    return directory / f"{name}.svg"
