from pathlib import Path

from ibis import _, row_number

from starplot.config import settings
from starplot.data import db
from starplot.data.catalog import Catalog
from starplot.data.translations import language_name_column


def table(
    language: str,
    catalog: Catalog | Path | str,
):
    con = db.connect()
    table_name = "constellations"

    if isinstance(catalog, Catalog):
        if not catalog.exists():
            catalog.download()
        c = con.read_parquet(str(catalog.path), table_name=table_name)
    else:
        c = con.read_parquet(str(catalog), table_name=table_name)

    name_column = language_name_column(language)
    if name_column not in c.columns:
        name_column = "name"

    return c.mutate(
        boundary=_.boundary.cast("geometry"),  # cast WKB to geometry type
        name=getattr(c, name_column),
        rowid=row_number(),
        sk=row_number(),
    )


def load(
    extent=None, 
    filters=None, 
    sql=None,
    catalog=None,
):
    filters = filters or []
    c = table(language=settings.language, catalog=catalog)

    if extent:
        filters.append(_.boundary.intersects(extent))

    if filters:
        c = c.filter(*filters)

    if sql:
        result = c.alias("_").sql(sql).select("sk").execute()
        skids = result["sk"].to_list()
        c = c.filter(_.sk.isin(skids))

    return c


def load_borders(extent=None, filters=None):
    filters = filters or []
    con = db.connect()
    c = con.table("constellation_borders")
    c = c.mutate(rowid=row_number())

    if extent:
        filters.append(_.geometry.intersects(extent))

    if filters:
        return c.filter(*filters)

    return c
