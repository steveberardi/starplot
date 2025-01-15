import zipfile

CRS = "+ellps=sphere +f=0 +proj=latlong +axis=wnu +a=6378137 +no_defs"


def zip_file(filename):
    zipped = zipfile.ZipFile(f"{filename}.zip", "w", zipfile.ZIP_DEFLATED)
    zipped.write(filename)
