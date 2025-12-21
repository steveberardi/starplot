import json

import pandas as pd
import pyarrow as pa

from starplot.data.translations import language_name_column

from data_settings import RAW_PATH, BUILD_PATH
from translations import get_translations


def read_properties():
    with open(RAW_PATH / "constellations.json", "r") as constellation_props_file:
        content = constellation_props_file.read()
        return json.loads(content)


def build():
    constellation_records = []

    translated = get_translations("constellation_names.csv")
    language_columns = [
        (language, language_name_column(language)) for language in translated.keys()
    ]

    for constellation_id, props in read_properties().items():
        row = {
            "iau_id": constellation_id,
            "name": props["name"],
        }
        for language, column_name in language_columns:
            row[column_name] = translated[language].get(constellation_id)

        constellation_records.append(row)

    df = pd.DataFrame.from_records(constellation_records)

    schema = pa.schema(
        [
            ("iau_id", pa.string()),
            ("name", pa.string()),
        ]
        + [(column_name, pa.string()) for _, column_name in language_columns]
    )

    df.to_parquet(
        BUILD_PATH / "constellation_names.parquet",
        engine="pyarrow",
        schema=schema,
        compression="snappy",
    )

    print("Constellation Names: " + str(len(constellation_records)))


if __name__ == "__main__":
    build()
