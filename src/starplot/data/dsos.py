from pathlib import Path

from ibis import _, row_number

from starplot.config import settings
from starplot.data import db, DataFiles
from starplot.data.catalog import Catalog
from starplot.data.translations import language_name_column


def table(
    language: str,
    catalog: Catalog | Path | str = DataFiles.ONGC,
):
    con = db.connect()
    table_name = "deep_sky_objects"

    if isinstance(catalog, Catalog):
        dsos = con.read_parquet(str(catalog.path), table_name=table_name)
    else:
        dsos = con.read_parquet(str(catalog), table_name=table_name)

    name_column = language_name_column(language, column_prefix="common_names")
    if name_column not in dsos.columns:
        name_column = "name"

    return dsos.mutate(
        geometry=_.geometry.cast("geometry"),  # cast WKB to geometry type
        common_names=getattr(dsos, name_column),
        rowid=row_number(),
        sk=row_number(),
    )


def load(extent=None, filters=None, sql=None):
    filters = filters or []
    dsos = table(language=settings.language)

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
