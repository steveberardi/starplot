import json

import numpy as np
import geopandas as gpd
import pandas as pd

from starplot.data import DataFiles
from starplot.data.dsos import ONGC_TYPE_MAP

COLUMNS = [
    "Name",
    "Type",
]

ongc = gpd.read_file(DataFiles.ONGC.value)
ongc = ongc.replace({np.nan: None})
dsos = []

for _, dso in ongc.iterrows():
    if not dso["geometry"]:
        continue

    d = {
        "Name": dso.Name,
        "Type": ONGC_TYPE_MAP.get(dso.Type),
        "RA": round(dso.ra_degrees / 15, 2),
        "DEC": round(dso.dec_degrees, 2),
        "Magnitude": dso["V-Mag"] or dso["B-Mag"] or "None",
        "Major Axis": dso.MajAx,
        "Minor Axis": dso.MinAx,
        "Angle": dso.PosAng,
        "Geometry": dso["geometry"].geom_type,
    }

    dsos.append(d)


with open("docs/data/ongc.json", "w") as outfile:
    outfile.write(json.dumps(dsos))
