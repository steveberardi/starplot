import csv
from pathlib import Path

from data_settings import RAW_PATH

TRANSLATIONS_PATH = RAW_PATH / "translations"


def walk_sub_directories(root_path):
    for p in root_path.iterdir():
        if p.is_dir():
            yield p


def get_translations(filename):
    """
    Returns dictionary in the following format:

    {
        "language_code": {
            "id_column": "translation"
        }
    }

    Where "id_column" is the column to join on (e.g. "iau_id" for constellations)

    """
    translations = {}

    for language_path in walk_sub_directories(TRANSLATIONS_PATH):
        language = str(language_path.name)

        translations[language] = {}

        with open(language_path / filename, "r") as langfile:
            reader = csv.reader(langfile)
            next(reader)
            for row in reader:
                translations[language][row[0]] = row[2]

    return translations
