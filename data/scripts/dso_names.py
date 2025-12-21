import json

import pandas as pd
import pyarrow as pa

from starplot.data.translations import language_name_column

from data_settings import RAW_PATH, BUILD_PATH
from translations import get_translations


def build():
    dso_records = []

    translated = get_translations("dso_names.csv")
    language_columns = [
        (language, language_name_column(language, column_prefix="common_names"))
        for language in translated.keys()
    ]

    for ongc_name, name in translated["en-us"].items():
        row = {
            "open_ngc_name": ongc_name,
            "name": name,
        }
        for language, column_name in language_columns:
            row[column_name] = translated[language].get(ongc_name)

        dso_records.append(row)

    df = pd.DataFrame.from_records(dso_records)

    schema = pa.schema(
        [
            ("open_ngc_name", pa.string()),
            ("name", pa.string()),
        ]
        + [(column_name, pa.string()) for _, column_name in language_columns]
    )

    df.to_parquet(
        BUILD_PATH / "dso_names.parquet",
        engine="pyarrow",
        schema=schema,
        compression="snappy",
    )

    print("DSO Names: " + str(len(dso_records)))


if __name__ == "__main__":
    build()
