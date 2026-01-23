import os
import shutil
import json

from starplot.data import DataFiles
from starplot.data.translations import LANGUAGES

import star_designations, constellation_names, dso_names
from data_settings import BUILD_PATH
from translations import get_label_dict


db_path = BUILD_PATH / "sky.db"


def build_all():
    # remove build directory, recreate it
    if os.path.exists(BUILD_PATH):
        shutil.rmtree(BUILD_PATH)
    os.makedirs(BUILD_PATH, exist_ok=True)

    star_designations.build()
    constellation_names.build()
    dso_names.build()

    # Copy database to starplot data library
    shutil.copy(BUILD_PATH / "star_designations.parquet", DataFiles.STAR_DESIGNATIONS)
    shutil.copy(
        BUILD_PATH / "constellation_names.parquet", DataFiles.CONSTELLATION_NAMES
    )
    shutil.copy(BUILD_PATH / "dso_names.parquet", DataFiles.DSO_NAMES)

    translations_terms = {}
    for language_code in LANGUAGES:
        translations_terms[language_code] = get_label_dict(language_code)

    with open(BUILD_PATH / "terms.json", "w", encoding="utf-8") as term_file:
        term_file.write(json.dumps(translations_terms, indent=4, ensure_ascii=False))


if __name__ == "__main__":
    build_all()
