import json

import numpy as np
import geopandas as gpd

from starplot.data import DataFiles
from starplot.data.dsos import ONGC_TYPE_MAP

COLUMNS = [
    "Name",
    "Type",
]

ongc = gpd.read_file(DataFiles.ONGC.value)
ongc = ongc.replace({np.nan: None})
dsos = []

for dso in ongc.itertuples():
    if not dso.geometry:
        continue

    d = {
        "Name": dso.name,
        "Type": ONGC_TYPE_MAP.get(dso.type),
        "RA": round(dso.ra_degrees / 15, 2),
        "DEC": round(dso.dec_degrees, 2),
        "Magnitude": dso.mag_v or dso.mag_b or "None",
        "Major Axis": dso.maj_ax,
        "Minor Axis": dso.min_ax,
        "Size": dso.size_deg2,
        "Geometry": dso.geometry.geom_type,
    }

    dsos.append(d)


with open("docs/data/ongc.json", "w") as outfile:
    outfile.write(json.dumps(dsos))
