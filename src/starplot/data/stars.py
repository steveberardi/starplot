from functools import cache
from pathlib import Path

from ibis import _, row_number
from starplot.config import settings
from starplot.data import db
from starplot.data.catalogs import Catalog, BIG_SKY_MAG11
from starplot.data.translations import language_name_column, LANGUAGE_NAME_COLUMNS


@cache
def table(
    catalog: Catalog | Path | str = BIG_SKY_MAG11,
    table_name="stars",
    language: str = "en-us",
):
    con = db.connect()

    if isinstance(catalog, Catalog):
        if not catalog.exists():
            catalog.download()
        stars = con.read_parquet(str(catalog.path), table_name=table_name)
    else:
        stars = con.read_parquet(str(catalog), table_name=table_name)

    stars = stars.mutate(
        geometry=_.geometry.cast("geometry"),  # cast WKB to geometry type
        rowid=row_number(),
        sk=row_number(),
    )

    designation_columns = ["name", "bayer", "flamsteed"] + LANGUAGE_NAME_COLUMNS
    designation_columns_missing = {
        col for col in designation_columns if col not in stars.columns
    }

    if designation_columns_missing:
        designations = con.table("star_designations")
        designations = designations.mutate(
            name=getattr(designations, language_name_column(language))
        )
        stars_joined = stars.join(
            designations,
            stars.hip == designations.hip,
            how="left",
        )
        stars = stars_joined.select(*stars.columns, *designation_columns_missing)

    return stars


def load(
    catalog: Catalog | Path | str,
    extent=None,
    filters=None,
    sql=None,
):
    filters = filters or []
    stars = table(catalog=catalog, language=settings.language)

    if extent:
        stars = stars.filter(stars.geometry.intersects(extent))

    if filters:
        stars = stars.filter(*filters)

    if sql:
        result = stars.alias("_").sql(sql).select("sk").execute()
        skids = result["sk"].to_list()
        stars = stars.filter(_.sk.isin(skids))

    return stars
