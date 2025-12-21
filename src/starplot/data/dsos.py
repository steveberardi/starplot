from functools import cache
from pathlib import Path

from ibis import _, row_number

from starplot.config import settings
from starplot.data import db
from starplot.data.catalogs import Catalog
from starplot.data.translations import (
    language_name_column,
    LANGUAGES,
)


@cache
def table(
    catalog: Catalog | Path | str,
    language: str,
):
    con = db.connect()
    table_name = "deep_sky_objects"

    if isinstance(catalog, Catalog):
        if not catalog.exists():
            catalog.download()
        dsos = con.read_parquet(str(catalog.path), table_name=table_name)
    else:
        dsos = con.read_parquet(str(catalog), table_name=table_name)

    name_column = language_name_column(language, column_prefix="common_names")
    name_columns = [
        language_name_column(lang, column_prefix="common_names") for lang in LANGUAGES
    ]
    name_columns_missing = {col for col in name_columns if col not in dsos.columns}

    if name_columns_missing and "name" in dsos.columns:
        dso_names = con.table("dso_names")
        dsos_joined = dsos.join(
            dso_names,
            dsos.name == dso_names.open_ngc_name,
            how="left",
        )
        dsos = dsos_joined.select(*dsos.columns, *name_columns_missing)

    if name_column not in dsos.columns:
        name_column = "name"

    return dsos.mutate(
        geometry=_.geometry.cast("geometry"),  # cast WKB to geometry type
        common_names=getattr(dsos, name_column),
        rowid=row_number(),
        sk=row_number(),
    )


def load(
    catalog: Catalog | Path | str,
    extent=None,
    filters=None,
    sql=None,
):
    filters = filters or []
    dsos = table(catalog=catalog, language=settings.language)

    if extent:
        dsos = dsos.filter(_.geometry.intersects(extent))

    filters.extend([_.ra.notnull() & _.dec.notnull()])

    if filters:
        dsos = dsos.filter(*filters)

    if sql:
        result = dsos.alias("_").sql(sql).select("sk").execute()
        skids = result["sk"].to_list()
        dsos = dsos.filter(_.sk.isin(skids))

    return dsos
