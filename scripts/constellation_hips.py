import pprint

from starplot.data import constellations


def get_constellation_hips():
    """
    Returns dictionary of constellations where:

        key = 3-letter abbreviation (e.g. "And")
        value = list of 2-element arrays that represent lines of the constellation
                each number is the HIP id: so [101, 201] would mean a line from
                HIP-101 to HIP-201
    """
    consdata = constellations.load()
    constellation_hips = {}

    for constellation, lines in consdata:
        cid = constellation.lower()

        constellation_hips[cid] = []

        for s1, s2 in lines:
            if [s1, s2] not in constellation_hips[cid] and [
                s2,
                s1,
            ] not in constellation_hips[cid]:
                constellation_hips[cid].append([s1, s2])
            else:
                print(cid)

    return constellation_hips


constellation_hips = get_constellation_hips()

pprint.pprint(constellation_hips)
