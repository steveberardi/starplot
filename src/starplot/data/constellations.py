from functools import cache
from pathlib import Path

from ibis import _, row_number

from starplot.config import settings
from starplot.data import db
from starplot.data.catalogs import Catalog
from starplot.data.translations import language_name_column, LANGUAGE_NAME_COLUMNS


@cache
def table(
    catalog: Catalog | Path | str,
    language: str,
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
    name_columns = ["name"] + LANGUAGE_NAME_COLUMNS
    name_columns_missing = {col for col in name_columns if col not in c.columns}

    if name_columns_missing and "iau_id" in c.columns:
        constellation_names = con.table("constellation_names")
        constellation_names = constellation_names.mutate(
            name=getattr(constellation_names, language_name_column(language))
        )
        constellations_joined = c.join(
            constellation_names,
            c.iau_id == constellation_names.iau_id,
            how="left",
        )
        c = constellations_joined.select(*c.columns, *name_columns_missing)

    if name_column not in c.columns:
        name_column = "name"

    return c.mutate(
        boundary=_.boundary.cast("geometry"),  # cast WKB to geometry type
        name=getattr(c, name_column),
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
    c = table(catalog=catalog, language=settings.language)

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
