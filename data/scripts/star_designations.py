import csv

import pandas as pd
import pyarrow as pa

from starplot.data.translations import language_name_column

from data_settings import RAW_PATH, BUILD_PATH
from translations import get_translations


def build():
    star_records = []

    translated = get_translations("star_names.csv")
    language_columns = [
        (language, language_name_column(language)) for language in translated.keys()
    ]

    with open(RAW_PATH / "star_designations.csv", "r") as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            star = row.copy()
            star["hip"] = int(star["hip"])
            star["flamsteed"] = (
                int(star["flamsteed"]) if star.get("flamsteed") else None
            )
            for language, column_name in language_columns:
                star[column_name] = translated[language].get(str(star["hip"]))

            star_records.append(star)

    df = pd.DataFrame.from_records(star_records)

    schema = pa.schema(
        [
            ("hip", pa.int64()),
            ("name", pa.string()),
            ("bayer", pa.string()),
            ("flamsteed", pa.int64()),
        ]
        + [(column_name, pa.string()) for _, column_name in language_columns]
    )

    df.to_parquet(
        BUILD_PATH / "star_designations.parquet",
        engine="pyarrow",
        schema=schema,
        compression="snappy",
    )

    print("Star Designations: " + str(len(star_records)))


if __name__ == "__main__":
    build()
