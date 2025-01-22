import json

import numpy as np


def create_dso_json():
    from starplot.models.dso import DSO_LEGEND_LABELS
    from starplot.data.dsos import load

    ongc = load().to_pandas()
    ongc = ongc.replace({np.nan: None})
    dsos = []

    for dso in ongc.itertuples():
        if not dso.geometry:
            continue

        d = {
            "Name": dso.name,
            "Type": DSO_LEGEND_LABELS.get(dso.type),
            "RA": round(dso.ra_degrees, 2),
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


def create_star_designation_json():
    from starplot import _
    from starplot.data.stars import load

    hip_stars = load(filters=[_.hip.notnull(), _.hip != 0]).to_pandas()
    hip_stars = hip_stars.replace({np.nan: None})
    stars = []

    for s in hip_stars.itertuples():
        if not any([s.name, s.bayer, s.flamsteed]):
            continue
        d = {
            "hip": s.hip,
            "name": s.name,
            "bayer": s.bayer,
            "flamsteed": s.flamsteed,
        }
        stars.append(d)

    with open("docs/data/star_designations.json", "w") as outfile:
        outfile.write(json.dumps(stars))


def create_constellations_json():
    from starplot import _
    from starplot.data.constellations import load

    df = load().to_pandas()
    df = df.replace({np.nan: None})
    constellations = []

    for con in df.itertuples():
        c = {
            "name": con.name,
            "iau_id": con.iau_id,
        }
        constellations.append(c)

    with open("docs/data/constellations.json", "w") as outfile:
        outfile.write(json.dumps(constellations))


def build():
    create_dso_json()
    create_star_designation_json()
    create_constellations_json()


if __name__ == "__main__":
    build()
