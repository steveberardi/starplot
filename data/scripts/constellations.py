import json

from shapely.geometry import Polygon

from starplot import Constellation
from starplot.data import Catalog
from starplot.data.translations import language_name_column

from data_settings import BUILD_PATH, RAW_PATH
from translations import get_translations

DATA_PATH = RAW_PATH / "iau"

translated = get_translations("constellation_names.csv")
language_columns = [
    (language, language_name_column(language)) for language in translated.keys()
]

# TODO : clean up data, consolidate

"""
External data dependencies:

constellations.json
constellation_names.csv (translations)
iau boundaries

"""


def parse_ra(ra_str):
    """Parses RA from border file HH MM SS to 0...360 degree float"""
    h, m, s = ra_str.strip().split(" ")
    return round(15 * (float(h) + float(m) / 60 + float(s) / 3600), 6)


def parse_dec(dec_str):
    """Parses DEC from ONGC CSV from HH:MM:SS to -90...90 degree float"""
    return round(float(dec_str), 6)


def parse_borders(constellation_id):
    coords = []

    with open(DATA_PATH / f"{constellation_id}.txt", "r") as borderfile:
        for line in borderfile.readlines():
            if "|" not in line:
                continue
            ra_str, dec_str, _ = line.split("|")
            ra = parse_ra(ra_str)
            dec = parse_dec(dec_str)
            coords.append((ra, dec))

    return Polygon(coords)


def read_properties():
    with open(RAW_PATH / "constellations.json", "r") as constellation_props_file:
        content = constellation_props_file.read()
        return json.loads(content)


def constellations():
    props_all = read_properties()

    for constellation_id, props in props_all.items():
        hiplines = props["hip_lines"]
        hip_ids = set()
        for hip_pair in hiplines:
            hip_ids.update(hip_pair)
        hip_ids = list(hip_ids)

        c = Constellation(
            name=props["name"],
            ra=props["ra"],
            dec=props["dec"],
            iau_id=constellation_id,
            constellation_id=constellation_id,
            star_hip_ids=hip_ids,
            star_hip_lines=hiplines,
            boundary=parse_borders(constellation_id),
        )
        for language, column_name in language_columns:
            setattr(c, column_name, translated[language].get(constellation_id))

        yield c


def build():
    name_columns = [column_name for _, column_name in language_columns]

    Catalog.build(
        objects=constellations(),
        path=BUILD_PATH / "constellations.parquet",
        chunk_size=100,
        columns=[
            "name",
            "ra",
            "dec",
            "iau_id",
            "constellation_id",
            "star_hip_ids",
            "star_hip_lines",
            "boundary",
        ]
        + name_columns,
        sorting_columns=[],
        compression="none",
        row_group_size=100,
    )
