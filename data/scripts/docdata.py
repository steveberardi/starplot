import json


def create_ongc_json():
    from starplot.models.dso import DSO, DSO_LEGEND_LABELS

    ongc = DSO.all()
    dsos = []

    for dso in ongc:
        if not dso.geometry:
            continue

        d = {
            "name": dso.name,
            "common_names": ", ".join(dso.common_names) if dso.common_names else "",
            "type": DSO_LEGEND_LABELS.get(dso.type),
            "ra": round(dso.ra, 2),
            "dec": round(dso.dec, 2),
            "magnitude": dso.magnitude if dso.magnitude else "None",
            "maj_ax": dso.maj_ax,
            "min_ax": dso.min_ax,
            "size": dso.size,
            "geom_type": dso.geometry.geom_type,
        }

        dsos.append(d)

    with open("docs/data/ongc.json", "w") as outfile:
        outfile.write(json.dumps(dsos))


def create_star_designation_json():
    from starplot import Star, _

    hip_stars = Star.find(where=[_.hip.notnull(), _.hip != 0])
    stars = []

    for s in hip_stars:
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
    from starplot import Constellation, _

    iau = Constellation.all()
    constellations = []

    for con in iau:
        c = {
            "name": con.name,
            "iau_id": con.iau_id,
        }
        constellations.append(c)

    with open("docs/data/constellations.json", "w") as outfile:
        outfile.write(json.dumps(constellations))


def build():
    create_ongc_json()
    create_star_designation_json()
    create_constellations_json()


if __name__ == "__main__":
    build()
