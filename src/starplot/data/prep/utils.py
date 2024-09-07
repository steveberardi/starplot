import zipfile
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent.parent.parent
RAW_DATA_PATH = ROOT / "raw"
BUILD_PATH = ROOT / "build"
DATA_LIBRARY = HERE.parent / "library"

CRS = "+ellps=sphere +f=0 +proj=latlong +axis=wnu +a=6378137 +no_defs"


def zip_file(filename):
    zipped = zipfile.ZipFile(f"{filename}.zip", "w", zipfile.ZIP_DEFLATED)
    zipped.write(filename)
